
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View

from orders.http_client import (
    invalidate_payment_sessions,
)
from orders.models import OrderProduct

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
