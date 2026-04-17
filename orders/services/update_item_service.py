from decimal import Decimal


class UpdateItemService:
    order_item_repository = None

    def __init__(self, order_item_repository, products_client, payments_client):
        self.order_item_repository = order_item_repository
        self.products_client = products_client
        self.payments_client = payments_client
    
    def execute(self, user, item_id: int, quantity: int):
        item = self.order_item_repository.get_item(item_id, user.id)
        
        if item is None:
            return {
                "success": False,
                "message": "El artículo seleccionado no existe en tu orden."
            }

        order = item.order
        stocks = self.products_client.get_products_stock([item.product_id])
        stock = stocks.get(str(item.product_id), 0)

        if not stock:
            self.order_item_repository.remove_item(item)
            return {
                "success": False,
                "message": "El producto ya no está disponible."
            }

        adjusted = False

        if stock <= 0:
            self.order_item_repository.remove_item(item)
            self.payments_client.invalidate_payment_sessions(order.id)

            order_total = self.order_item_repository.calculate_total(order)

            return {
                "success": True,
                "message": "Producto no disponible.",
                "order_total": _format_amount(order_total),
                "order_empty": order_total == Decimal("0.00"),
                "removed": True,
                "available_stock": 0,
            }

        if quantity > stock:
            quantity = stock
            adjusted = True

        self.order_item_repository.update_quantity(item, quantity)

        self.payments_client.invalidate_payment_sessions(order.id)

        item_total = item.product_price * item.quantity
        order_total = self.order_item_repository.calculate_total(order)
        
        return {
            "success": True,
            "message": "Actualizado.",
            "quantity": item.quantity,
            "item_total": _format_amount(item_total),
            "order_total": _format_amount(order_total),
            "adjusted": adjusted,
            "removed": False,
            "order_empty": order_total == Decimal("0.00"),
            "available_stock": stock,
        }
        
def _format_amount(value):
    if value is None:
        value = Decimal("0.00")
    return f"{value:.2f}"