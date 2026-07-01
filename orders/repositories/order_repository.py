from typing import Optional

from orders.domain.entities import OrderEntity, OrderItemEntity
from orders.models import Order, OrderProduct


class OrderRepository:
    def get_order_with_items(self, order_id: int) -> Optional[Order]:
        try:
            return Order.objects.prefetch_related("items").get(pk=order_id)
        except Order.DoesNotExist:
            return None

    def get_active_order(self, user_id: int) -> Optional[OrderEntity]:
        order = Order.objects.filter(
            is_active=True, user_id=user_id
        ).prefetch_related("items").first()
        if order is None:
            return None
        return self._to_entity(order)

    def get_by_id(self, order_id: int) -> Optional[OrderEntity]:
        try:
            order = Order.objects.prefetch_related("items").get(pk=order_id)
            return self._to_entity(order)
        except Order.DoesNotExist:
            return None

    def save(self, order: OrderEntity) -> None:
        if order.id is None:
            django_order = Order.objects.create(
                user_id=order.user_id,
                user_username=order.user_username,
                user_email=order.user_email,
                is_active=order.is_active,
            )
            order.id = django_order.id
        else:
            django_order = Order.objects.get(pk=order.id)
            django_order.user_username = order.user_username
            django_order.user_email = order.user_email
            django_order.is_active = order.is_active
            django_order.save(update_fields=["user_username", "user_email", "is_active"])

        existing = {i.product_id: i for i in django_order.items.all()}
        kept_ids = set()

        for item_entity in order.items:
            kept_ids.add(item_entity.product_id)
            if item_entity.product_id in existing:
                db_item = existing[item_entity.product_id]
                if (
                    db_item.quantity != item_entity.quantity
                    or db_item.product_name != item_entity.product_name
                    or db_item.product_price != item_entity.product_price
                ):
                    OrderProduct.objects.filter(pk=db_item.pk).update(
                        product_name=item_entity.product_name,
                        product_price=item_entity.product_price,
                        quantity=item_entity.quantity,
                    )
            else:
                created = OrderProduct.objects.create(
                    order=django_order,
                    product_id=item_entity.product_id,
                    product_name=item_entity.product_name,
                    product_price=item_entity.product_price,
                    quantity=item_entity.quantity,
                )
                item_entity.id = created.id

        django_order.items.exclude(product_id__in=kept_ids).delete()

    def _to_entity(self, order: Order) -> OrderEntity:
        return OrderEntity(
            id=order.id,
            user_id=order.user_id,
            user_username=order.user_username,
            user_email=order.user_email,
            is_active=order.is_active,
            items=[
                OrderItemEntity(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    product_price=item.product_price,
                    quantity=item.quantity,
                )
                for item in order.items.all()
            ],
        )
