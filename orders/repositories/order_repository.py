from typing import Optional

from django.db import transaction

from orders.models import Order


class OrderRepository:
    def get_active_order(self, user_id: int) -> Optional[Order]:
        return Order.objects.filter(
            is_active=True, 
            user_id=user_id
        ).prefetch_related("items").first()

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        try:
            return Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return None

    def get_order_with_items(self, order_id: int) -> Optional[Order]:
        try:
            return Order.objects.prefetch_related("items").get(pk=order_id)
        except Order.DoesNotExist:
            return None

    @transaction.atomic
    def create_or_get_active(self, user_id: int, username: str, email: str) -> Order:
        order, created = Order.objects.get_or_create(
            is_active=True,
            user_id=user_id,
            defaults={
                "user_username": username,
                "user_email": email,
            }
        )
        return order

    def mark_as_paid(self, order_id: int) -> bool:
        rows = Order.objects.filter(
            id=order_id, 
            is_active=True
        ).update(is_active=False)
        return rows > 0

    def update_user_info(self, order: Order, username: str, email: str) -> None:
        order.user_username = username
        order.user_email = email
        order.save(update_fields=["user_username", "user_email"])