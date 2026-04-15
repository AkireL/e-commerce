from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View
from django.db.models import DecimalField, ExpressionWrapper, F, Sum


from orders.http_client import (
    get_products_stock,
    invalidate_payment_sessions,
)
from orders.models import OrderProduct

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


def _format_amount(value):
    if value is None:
        value = Decimal("0.00")
    return f"{value:.2f}"

def _error_response(request, message, status=400):
    if _is_ajax(request):
        return JsonResponse({"success": False, "message": message}, status=status)
    messages.error(request, message)
    return redirect("orders:my-orders")

def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _calculate_order_total(order):
    total = order.items.annotate(
        line_total=ExpressionWrapper(
            F("product_price") * F("quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    ).aggregate(total=Sum("line_total"))
    return total.get("total") or Decimal("0.00")
