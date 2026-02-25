from typing import Optional

from orders.models import Order, OrderProduct


def _build_item_dict(item: OrderProduct) -> dict:
    return {
        'id': item.id,
        'product_id': item.product_id,
        'product_name': item.product_name,
        'product_price': item.product_price,
        'quantity': item.quantity,
    }


def _build_order_dict(order: Order, items: list[OrderProduct] | None = None) -> dict:
    if items is None:
        items = list(order.items.all())
    
    return {
        'id': order.id,
        'user_id': order.user_id,
        'user_username': order.user_username,
        'user_email': order.user_email,
        'is_active': order.is_active,
        'items': [_build_item_dict(item) for item in items],
    }


def get_active_order_for_user(user_id: int) -> Optional[dict]:
    order = Order.objects.filter(is_active=True, user_id=user_id).first()
    if order is None:
        return None
    return _build_order_dict(order)


def get_order_by_id(order_id: int) -> Optional[dict]:
    try:
        order = Order.objects.get(pk=order_id)
        return _build_order_dict(order)
    except Order.DoesNotExist:
        return None


def mark_order_as_paid(order_id: int) -> bool:
    rows = Order.objects.filter(id=order_id, is_active=True).update(is_active=False)
    return rows > 0
