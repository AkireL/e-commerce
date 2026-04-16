from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View

from orders.http_client import (
    get_products_stock,
    invalidate_payment_sessions,
)
from orders.repositories import OrderItemRepository

order_item_repository = OrderItemRepository()


class UpdateOrderItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        quantity_raw = request.POST.get("quantity")
        quantity = 0

        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return _error_response("La cantidad debe ser un número válido.")

        if quantity < 1:
            return _error_response("La cantidad debe ser al menos 1.")

        item = order_item_repository.get_item(pk, request.user.id)
        
        if item is None:
            return _error_response("El artículo seleccionado no existe en tu orden.", status=404)

        order = item.order
        stocks = get_products_stock([item.product_id])
        stock = stocks.get(str(item.product_id), 0)

        if not stock:
            order_item_repository.remove_item(item)
            return _error_response(request, "El producto ya no está disponible.", status=404)

        adjusted = False

        if stock <= 0:
            order_item_repository.remove_item(item)
            invalidate_payment_sessions(order.id)
            order_total = order_item_repository.calculate_total(order)
            message = "Retiramos este producto de tu carrito porque ya no está disponible."

            return JsonResponse({
                "success": True,
                "order_total": _format_amount(order_total),
                "order_empty": order_total == Decimal("0.00"),
                "removed": True,
                "available_stock": 0,
                "message": message,
            })

        if quantity > stock:
            quantity = stock
            adjusted = True

        order_item_repository.update_quantity(item, quantity)

        invalidate_payment_sessions(order.id)

        item_total = item.product_price * item.quantity
        order_total = order_item_repository.calculate_total(order)
        response_message = "Actualizamos la cantidad para ti." if adjusted else "Cantidad actualizada."
        
        response_data = {
            "success": True,
            "quantity": item.quantity,
            "item_total": _format_amount(item_total),
            "order_total": _format_amount(order_total),
            "adjusted": adjusted,
            "removed": False,
            "order_empty": order_total == Decimal("0.00"),
            "available_stock": stock,
            "message": response_message,
        }

        return JsonResponse(response_data)

def _format_amount(value):
    if value is None:
        value = Decimal("0.00")
    return f"{value:.2f}"

def _error_response( message, status=400):
    return JsonResponse({"success": False, "message": message}, status=status)
