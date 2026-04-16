from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View

from orders.http_client import invalidate_payment_sessions
from orders.repositories import OrderRepository, OrderItemRepository


order_repository = OrderRepository()
order_item_repository = OrderItemRepository()


class RemoveOrderItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = order_item_repository.get_item(pk, request.user.id)
        
        if item is None:
            return _error_response(request, "El artículo que intentas eliminar no existe.", status=404)

        order = item.order
        product_name = item.product_name

        order_item_repository.remove_item(item)
        invalidate_payment_sessions(order.id)

        order_total = order_item_repository.calculate_total(order)
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


def _error_response(request, message, status=400):
    if _is_ajax(request):
        return JsonResponse({"success": False, "message": message}, status=status)
    messages.error(request, message)
    return redirect("orders:my-orders")