from decimal import Decimal
from typing import Iterable

from django.db import transaction

from orders.models import Order

from .exceptions import EmptyOrderError
from .models import PaymentItem, PaymentSession, PaymentSessionStatus


def _clone_order_items(session: PaymentSession, order_items: Iterable) -> Decimal:
    """Copia los artículos de la orden dentro de la sesión y calcula el total."""

    items_to_create = []
    total = Decimal("0.00")

    for order_item in order_items:
        price = order_item.product_price
        line_total = price * order_item.quantity
        total += line_total
        items_to_create.append(
            PaymentItem(
                session=session,
                product_id=order_item.product_id,
                product_name=order_item.product_name,
                unit_price=price,
                quantity=order_item.quantity,
            )
        )

    PaymentItem.objects.bulk_create(items_to_create)
    return total

def create_payment_session(order: Order, user_id: int, username: str, email: str) -> PaymentSession:
    """Genera una nueva sesión de pago para la orden especificada."""

    order_items = order.items.all()

    if not order_items.exists():
        raise EmptyOrderError("La orden no tiene productos para pagar.")

    with transaction.atomic():
        pending_session = (
            PaymentSession.objects.filter(order_id=order.id, status=PaymentSessionStatus.PENDING)
            .select_for_update()
            .first()
        )

        if pending_session:
            session = pending_session
            session.items.all().delete()
        else:
            session = PaymentSession.objects.create(
                order_id=order.id,
                order_number=str(order.id),
                user_id=user_id,
                user_username=username,
                user_email=email,
                status=PaymentSessionStatus.PENDING,
            )

        total = _clone_order_items(session, order_items)
        session.amount_total = total
        session.save(update_fields=["order_number", "user_username", "user_email", "status", "amount_total", "updated_at"])

    return session
