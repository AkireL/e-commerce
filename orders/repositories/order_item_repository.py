from decimal import Decimal
from typing import Optional

from django.db.models import DecimalField, ExpressionWrapper, F, Sum

from orders.models import Order, OrderProduct


class OrderItemRepository:
    def get_item(self, item_id: int, user_id: int, is_active: bool = True) -> Optional[OrderProduct]:
        try:
            return OrderProduct.objects.get(
                pk=item_id,
                order__user_id=user_id,
                order__is_active=is_active,
            )
        except OrderProduct.DoesNotExist:
            return None

    def get_items_for_order(self, order: Order) -> list[OrderProduct]:
        return list(order.items.all())

    def add_or_update_item(
        self, 
        order: Order, 
        product_id: int, 
        product_name: str, 
        product_price: Decimal, 
        quantity: int
    ) -> tuple[OrderProduct, bool]:
        item, created = order.items.get_or_create(
            product_id=product_id,
            product_name=product_name,
            product_price=product_price,
            defaults={"quantity": quantity}
        )
        
        if not created:
            self.update_quantity(item, quantity)
            
        return item, created

    def update_quantity(self, item: OrderProduct, quantity: int) -> None:
        item.quantity = quantity
        item.save(update_fields=["quantity"])

    def remove_item(self, item: OrderProduct) -> None:
        item.delete()

    def calculate_total(self, order: Order) -> Decimal:
        total = order.items.annotate(
            line_total=ExpressionWrapper(
                F("product_price") * F("quantity"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        ).aggregate(total=Sum("line_total"))
        return total.get("total") or Decimal("0.00")