import uuid
from decimal import Decimal
from typing import Optional


from payments.models import PaymentItem, PaymentSession, PaymentSessionStatus
from django.utils import timezone
from django.db import transaction
from payments.exceptions import EmptyOrderError
    

def _build_item_info(item: PaymentItem) -> dict:
    return {
        'id': item.id,
        'product_id': item.product_id,
        'product_name': item.product_name,
        'unit_price': item.unit_price,
        'quantity': item.quantity,
        'line_total': item.unit_price * item.quantity,
    }


def _build_session_info(session: PaymentSession, items: list[PaymentItem] | None = None) -> dict:
    if items is None:
        items = list(session.items.all())
    
    return {
        'id': session.id,
        'token': session.token,
        'order_id': session.order_id,
        'order_number': session.order_number,
        'user_id': session.user_id,
        'user_username': session.user_username,
        'user_email': session.user_email,
        'status': session.status,
        'amount_total': session.amount_total,
        'items': [_build_item_info(item) for item in items],
        'get_checkout_url': lambda: f"/payments/checkout/{session.token}/",
    }


def get_session_by_token(token: uuid.UUID) -> Optional[dict]:
    try:
        session = PaymentSession.objects.prefetch_related("items").get(token=token)
        return _build_session_info(session)
    except PaymentSession.DoesNotExist:
        return None


def get_completed_session(token: uuid.UUID, user_id: int) -> Optional[dict]:
    try:
        session = PaymentSession.objects.prefetch_related("items").get(
            token=token,
            user_id=user_id,
            status=PaymentSessionStatus.COMPLETED,
        )
        return _build_session_info(session)
    except PaymentSession.DoesNotExist:
        return None


def get_pending_session_for_checkout(
    token: uuid.UUID, user_id: int, username: str, email: str
) -> Optional[dict]:
    try:
        session = PaymentSession.objects.prefetch_related("items").get(
            token=token,
            user_id=user_id,
            user_username=username,
            user_email=email,
        )
        return _build_session_info(session)
    except PaymentSession.DoesNotExist:
        return None


def invalidate_pending_sessions(order_id: int) -> int:
    return PaymentSession.objects.filter(
        order_id=order_id,
        status=PaymentSessionStatus.PENDING
    ).delete()[0]


def create_payment_session(
    order_data: dict, user_id: int, username: str, email: str
) -> dict:
    items = order_data.get('items', [])
    
    if not items:
        raise EmptyOrderError("La orden no tiene productos para pagar.")
    
    order_id = order_data.get('id')
    
    with transaction.atomic():
        pending_session = (
            PaymentSession.objects.filter(order_id=order_id, status=PaymentSessionStatus.PENDING)
            .select_for_update()
            .first()
        )

        if pending_session:
            session = pending_session
            session.items.all().delete()
        else:
            session = PaymentSession.objects.create(
                order_id=order_id,
                order_number=str(order_id),
                user_id=user_id,
                user_username=username,
                user_email=email,
                status=PaymentSessionStatus.PENDING,
            )

        total = _clone_order_items(session, items)
        session.amount_total = total
        session.save(update_fields=["order_number", "user_username", "user_email", "status", "amount_total", "updated_at"])

    return _build_session_info(session)


def _clone_order_items(session: PaymentSession, order_items: list[dict]) -> Decimal:
    items_to_create = []
    total = Decimal("0.00")

    for item in order_items:
        price_str = str(item['product_price']).strip()
        price = Decimal(price_str)
        quantity = int(item['quantity'])
        line_total = price * quantity
        total += line_total
        items_to_create.append(
            PaymentItem(
                session=session,
                product_id=item['product_id'],
                product_name=item['product_name'],
                unit_price=price,
                quantity=quantity,
            )
        )

    PaymentItem.objects.bulk_create(items_to_create)
    return total


def complete_payment_session(token: uuid.UUID) -> Optional[dict]:    
    try:
        session = PaymentSession.objects.get(token=token)
        session.status = PaymentSessionStatus.COMPLETED
        session.completed_at = timezone.now()
        session.save(update_fields=["status", "completed_at", "updated_at"])
        return _build_session_info(session)
    except PaymentSession.DoesNotExist:
        return None
