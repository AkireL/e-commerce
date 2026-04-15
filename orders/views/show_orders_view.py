from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from orders.models import Order
from orders.http_client import (
    get_products_info,
)

class MyOrdersView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'my_orders.html'
    context_object_name = "order"

    def get_object(self):
        return Order.objects.filter(
            is_active=True, 
            user_id=self.request.user.id
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context.get("order")

        if order:
            items = list(order.items.all())
            total = sum((item.line_total for item in items), Decimal("0.00"))
            
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
