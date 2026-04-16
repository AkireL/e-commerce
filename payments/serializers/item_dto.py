
class ItemDTO:
    def __call__(self, item):
        return {
            'id': item.id,
            'product_id': item.product_id,
            'product_name': item.product_name,
            'unit_price': item.unit_price,
            'quantity': item.quantity,
            'line_total': item.unit_price * item.quantity,
        }