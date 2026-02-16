from decimal import Decimal
from typing import Iterable

from django.db import transaction

from orders.models import OrderProduct

from .exceptions import EmptyOrderError
from .models import PaymentItem, PaymentSession, PaymentSessionStatus


def _clone_order_items(session: PaymentSession, order_items: Iterable[OrderProduct]) -> Decimal:
    """Copia los artículos de la orden dentro de la sesión y calcula el total."""

    items_to_create = []
    total = Decimal("0.00")

    for order_item in order_items:
        price = order_item.product.price
        line_total = price * order_item.quantity
        total += line_total
        items_to_create.append(
            PaymentItem(
                session=session,
                product_id=order_item.product.id,
                product_name=order_item.product.name,
                unit_price=price,
                quantity=order_item.quantity,
            )
        )

    PaymentItem.objects.bulk_create(items_to_create)
    return total


def create_payment_session(order, user) -> PaymentSession:
    """Genera una nueva sesión de pago para la orden especificada."""

    order_items = order.orderproduct_set.select_related("product")

    if not order_items.exists():
        raise EmptyOrderError("La orden no tiene productos para pagar.")

    with transaction.atomic():
        pending_session = order.payment_sessions.filter(status=PaymentSessionStatus.PENDING).select_for_update().first()

        if pending_session:
            session = pending_session
            session.items.all().delete()
        else:
            session = PaymentSession.objects.create(order=order, user=user)

        total = _clone_order_items(session, order_items)
        session.amount_total = total
        session.save(update_fields=["amount_total", "updated_at"])

    return session
