from orders.models import Order
from orders.http_client import get_products_info

class ShowOrderService:
    
    def __init__(self, order_repository, order_item_repository):
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository
    
    def get_order(self, user_id):
        return self.order_repository.get_active_order(user_id)
    
    def _calculate_total(self, order: Order):
        return self.order_item_repository.calculate_total(order)
    
    def get_items(self, order: Order):
        order_items = self.order_item_repository.get_items_for_order(order)
        
        product_ids = [item.product_id for item in order_items]
        products = get_products_info(product_ids)
        
        items = []
        for item in order_items:
            product_data = products.get(str(item.product_id)) or {}

            item_dict = {
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
            items.append(item_dict)
            
        return {
            "order_items": items,
            "oredr_total": self._calculate_total(order),
        }
    