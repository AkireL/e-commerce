from decimal import Decimal

from orders.http_client import invalidate_payment_sessions


class RemoveItemService:

    def __init__(self, order_item_repository):
        self.order_item_repository = order_item_repository

    def execute(self, user, item_id):
        item = self.order_item_repository.get_item(item_id, user.id)
        
        if item is None:
            return {
                "success": False,
                "message": "El artículo que intentas eliminar no existe.",
            }
        
        order = item.order
        product_name = item.product_name

        self.order_item_repository.remove_item(item)
        invalidate_payment_sessions(order.id)

        order_total = self.order_item_repository.calculate_total(order)
        order_empty = order_total == Decimal("0.00")

        return {
            "success": True,
            "message": f"{product_name} fue eliminado del carrito.",
            "order_total": _format_amount(order_total),
            "order_empty": order_empty,
        }

def _format_amount(value):
    if value is None:
        value = Decimal("0.00")
    return f"{value:.2f}"