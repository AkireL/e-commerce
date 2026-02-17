from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import FormView, DetailView, TemplateView

from payments.models import PaymentSession, PaymentSessionStatus
from products.models import Product

from .forms import OrderProductForm
from .models import Order, OrderProduct

class MyOrdersView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'my_orders.html'
    context_object_name = "order"

    def get_object(self):
        return Order.objects.filter(
            is_active=True, 
            user_id=self.request.user.id).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context.get("order")

        if order:
            items = list(order.items.all())
            total = sum((item.line_total for item in items), Decimal("0.00"))
            
            product_ids = [item.product_id for item in items]
            products = {
                p.id: p for p in Product.objects.filter(id__in=product_ids)
            }
            
            for index, item in enumerate(items):
                items[index].product = products.get(item.product_id)
                
            
            context.update(
                {
                    "order_items": items,
                    "order_total": total,
                }
            )

        context.setdefault("order_items", [])
        context.setdefault("order_total", Decimal("0.00"))

        return context
    
class CreateOrderProductView(LoginRequiredMixin, FormView):
    template_name="create_order_product.html"
    form_class = OrderProductForm
    success_url = reverse_lazy('my-orders')

    def form_valid(self, form):
        order, _ = Order.objects.get_or_create(
            is_active=True,
            user_id=self.request.user.id,
        )

        quantity = form.cleaned_data["quantity"]
        product = form.cleaned_data["product"]
        
        order_product, created = order.items.get_or_create(
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            defaults={"quantity": quantity}
        )

        if not created:
            order.items.filter(pk=order_product.pk).update(quantity=quantity)
            order_product.refresh_from_db(fields=["quantity"])

        self.object = order_product
        return HttpResponseRedirect(self.get_success_url())


class OrderProcessedView(LoginRequiredMixin, TemplateView):
    template_name = "order_processed.html"

    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get("token")
        self.session = self._get_session(token, request)
        return super().dispatch(request, *args, **kwargs)

    def _get_session(self, token, request):
        
        # TODO: Order no debe consumir directamente los modelos del modulo pago dado que son de diferente dominio
        return get_object_or_404(
            self._session_queryset(),
            token=token,
            user_id=request.user.id,
            status=PaymentSessionStatus.COMPLETED,
        )


    def _session_queryset(self):
        # TODO: Order no debe consumir directamente los modelos del modulo pago dado que son de diferente dominio
        return PaymentSession.objects.prefetch_related("items")
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.session.order_id
        items = self.session.items.all()
        context.update(
            {
                "session": self.session,
                "order": order_id,
                "items": items,
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


def _invalidate_pending_sessions(order):
    PaymentSession.objects.filter(
        order_id=order.id,
        status=PaymentSessionStatus.PENDING
    ).delete()


def _error_response(request, message, status=400):
    if _is_ajax(request):
        return JsonResponse({"success": False, "message": message}, status=status)
    messages.error(request, message)
    return redirect("my-orders")


@login_required
@require_POST
def update_order_item(request, pk):
    try:
        order_item = OrderProduct.objects.get(
            pk=pk,
            order__user_id=request.user.id,
            order__is_active=True,
        )
    except OrderProduct.DoesNotExist:
        return _error_response(request, "El artículo seleccionado no existe en tu orden.", status=404)

    order = order_item.order

    try:
        product = Product.objects.get(pk=order_item.product_id)
    except Product.DoesNotExist:
        order_item.delete()
        return _error_response(request, "El producto ya no está disponible.", status=404)

    quantity_raw = request.POST.get("quantity")
    try:
        quantity = int(quantity_raw)
    except (TypeError, ValueError):
        return _error_response(request, "La cantidad debe ser un número válido.")

    if quantity < 1:
        return _error_response(request, "La cantidad debe ser al menos 1.")

    stock = product.stock
    adjusted = False

    if stock <= 0:
        order_item.delete()
        _invalidate_pending_sessions(order)
        order_total = _calculate_order_total(order)
        message = "Retiramos este producto de tu carrito porque ya no está disponible."
        if _is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "order_total": _format_amount(order_total),
                    "order_empty": order_total == Decimal("0.00"),
                    "removed": True,
                    "available_stock": 0,
                    "message": message,
                }
            )
        messages.warning(request, message)
        return redirect("my-orders")

    if quantity > stock:
        quantity = stock
        adjusted = True

    order_item.quantity = quantity
    order_item.save(update_fields=["quantity"])

    _invalidate_pending_sessions(order)

    item_total = product.price * order_item.quantity
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
    return redirect("my-orders")


@login_required
@require_POST
def remove_order_item(request, pk):
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
    _invalidate_pending_sessions(order)

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
    return redirect("my-orders")
