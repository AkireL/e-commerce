from decimal import Decimal
import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, TemplateView, View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .forms import OrderProductForm
from .http_client import (
    get_payment_completed_session,
    get_products_available,
    get_products_info,
    get_products_stock,
    invalidate_payment_sessions,
)
from .models import Order, OrderProduct

class MyOrdersView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'my_orders.html'
    context_object_name = "order"

    def get_object(self):
        return Order.objects.filter(
            is_active=True, 
            user_id=self.request.user.id
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context.get("order")

        if order:
            items = list(order.items.all())
            total = sum((item.line_total for item in items), Decimal("0.00"))
            
            product_ids = [item.product_id for item in items]
            products = get_products_info(product_ids)
            
            enriched_items = []
            for item in items:
                product_data = products.get(str(item.product_id)) or {}
                item_dict = {
                    "pk": item.id,
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "product_price": item.product_price,
                    "quantity": item.quantity,
                    "line_total": item.line_total,
                    "product": {
                        "stock": product_data.get("stock", 0),
                        "photo_url": product_data.get("photo_url"),
                    },
                }
                enriched_items.append(item_dict)
            
            context.update(
                {
                    "order_items": enriched_items,
                    "order_total": total,
                }
            )

        context.setdefault("order_items", [])
        context.setdefault("order_total", Decimal("0.00"))

        return context

class CreateOrderProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = OrderProductForm(request.data, products=get_products_available())
        
        if not form.is_valid():
            errors = list(form.errors.values())
            return Response({
                'success': False,
                'message': errors[0][0] if errors else 'Formulario inválido'
            }, status=status.HTTP_400_BAD_REQUEST)

        order, _ = Order.objects.get_or_create(
            is_active=True,
            user_id=request.user.id,
        )

        quantity = form.cleaned_data["quantity"]
        product_id = int(form.cleaned_data["product"])
        product_data = form.get_product_data(product_id)

        if not product_data:
            return Response({
                'success': False,
                'message': 'Producto no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

        order_product, created = order.items.get_or_create(
            product_id=product_id,
            product_name=product_data['name'],
            product_price=product_data['price'],
            defaults={"quantity": quantity}
        )

        if not created:
            order.items.filter(pk=order_product.pk).update(quantity=quantity)
            order_product.refresh_from_db(fields=["quantity"])

        return Response({
            'success': True,
            'message': f'El producto "{product_data["name"]}" se ha agregado al carrito',
            'quantity': order_product.quantity
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class OrderProcessedView(LoginRequiredMixin, TemplateView):
    template_name = "order_processed.html"

    def dispatch(self, request, *args, **kwargs):
        token_raw = kwargs.get("token")
        if token_raw is None:
            messages.error(request, "Token no proporcionado.")
            return redirect("orders:my-orders")
        
        try:
            token = uuid.UUID(str(token_raw))
        except (ValueError, AttributeError):
            messages.error(request, "Token inválido.")
            return redirect("orders:my-orders")
        
        self.session_data = get_payment_completed_session(str(token), request.user.id)
        if self.session_data is None:
            return redirect("orders:my-orders")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        
        context.update(
            {
                "session": self.session_data,
                "order": self.session_data.get("order_id"),
                "items": self.session_data.get("items", []),
            }
        )
        return context


def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _format_amount(value):
    if value is None:
        value = Decimal("0.00")
    return f"{value:.2f}"


def _calculate_order_total(order):
    total = order.items.annotate(
        line_total=ExpressionWrapper(
            F("product_price") * F("quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    ).aggregate(total=Sum("line_total"))
    return total.get("total") or Decimal("0.00")


def _error_response(request, message, status=400):
    if _is_ajax(request):
        return JsonResponse({"success": False, "message": message}, status=status)
    messages.error(request, message)
    return redirect("orders:my-orders")

class UpdateOrderItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            order_item = OrderProduct.objects.get(
                pk=pk,
                order__user_id=request.user.id,
                order__is_active=True,
            )
        except OrderProduct.DoesNotExist:
            return _error_response(request, "El artículo seleccionado no existe en tu orden.", status=404)

        order = order_item.order
        stocks = get_products_stock([order_item.product_id])
        stock = stocks.get(str(order_item.product_id), 0)

        if not stock:
            order_item.delete()
            return _error_response(request, "El producto ya no está disponible.", status=404)

        quantity_raw = request.POST.get("quantity")
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return _error_response(request, "La cantidad debe ser un número válido.")

        if quantity < 1:
            return _error_response(request, "La cantidad debe ser al menos 1.")

        adjusted = False

        if stock <= 0:
            order_item.delete()
            invalidate_payment_sessions(order.id)
            order_total = _calculate_order_total(order)
            message = "Retiramos este producto de tu carrito porque ya no está disponible."
            if _is_ajax(request):
                return JsonResponse({
                    "success": True,
                    "order_total": _format_amount(order_total),
                    "order_empty": order_total == Decimal("0.00"),
                    "removed": True,
                    "available_stock": 0,
                    "message": message,
                })
            messages.warning(request, message)
            return redirect("orders:my-orders")

        if quantity > stock:
            quantity = stock
            adjusted = True

        order_item.quantity = quantity
        order_item.save(update_fields=["quantity"])

        invalidate_payment_sessions(order.id)

        item_total = order_item.product_price * order_item.quantity
        order_total = _calculate_order_total(order)
        response_message = "Actualizamos la cantidad para ti." if adjusted else None

        response_data = {
            "success": True,
            "quantity": order_item.quantity,
            "item_total": _format_amount(item_total),
            "order_total": _format_amount(order_total),
            "adjusted": adjusted,
            "removed": False,
            "order_empty": order_total == Decimal("0.00"),
            "available_stock": stock,
            "message": response_message,
        }

        if _is_ajax(request):
            return JsonResponse(response_data)

        if adjusted:
            messages.info(request, response_message)
        else:
            messages.success(request, "Cantidad actualizada.")
        return redirect("orders:my-orders")


class RemoveOrderItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            order_item = OrderProduct.objects.get(
                pk=pk,
                order__user_id=request.user.id,
                order__is_active=True,
            )
        except OrderProduct.DoesNotExist:
            return _error_response(request, "El artículo que intentas eliminar no existe.", status=404)

        order = order_item.order
        product_name = order_item.product_name

        order_item.delete()
        invalidate_payment_sessions(order.id)

        order_total = _calculate_order_total(order)
        order_empty = order_total == Decimal("0.00")

        response_data = {
            "success": True,
            "order_total": _format_amount(order_total),
            "order_empty": order_empty,
            "message": f"{product_name} fue eliminado del carrito.",
        }

        if _is_ajax(request):
            return JsonResponse(response_data)

        messages.success(request, response_data["message"])
        return redirect("orders:my-orders")
