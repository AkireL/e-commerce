from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from orders.http_client import get_products_info
from orders.repositories import OrderRepository, OrderItemRepository

order_repository = OrderRepository()
order_item_repository = OrderItemRepository()


class MyOrdersView(LoginRequiredMixin, DetailView):
    model = None
    template_name = 'my_orders.html'
    context_object_name = "order"

    def get_object(self):
        return order_repository.get_active_order(self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context.get("order")

        if order:
            items = order_item_repository.get_items_for_order(order)
            total = order_item_repository.calculate_total(order)
            
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