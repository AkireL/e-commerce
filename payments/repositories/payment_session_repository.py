import uuid
from typing import Optional

from django.utils import timezone
from django.db import transaction

from payments.exceptions import EmptyOrderError
from payments.models import PaymentSession, PaymentSessionStatus
from payments.serializers.session_dto import SessionDTO


class PaymentSessionRepository:
    def __init__(self, payment_item_repository):
        self.payment_item_repository = payment_item_repository

    def create_payment_session(self, order_data: dict, user) -> dict:
        items = order_data["items"]

        if not items:
            raise EmptyOrderError("La orden no tiene productos para pagar.")

        order_id = order_data["id"]

        with transaction.atomic():
            pending_session = (
                PaymentSession.objects.filter(
                    order_id=order_id, status=PaymentSessionStatus.PENDING
                )
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
                    user_id=user.id,
                    user_username=user.username,
                    user_email=user.email,
                    status=PaymentSessionStatus.PENDING,
                )

            total = self.payment_item_repository.bulk_create(session, items)
            session.amount_total = total
            session.save(
                update_fields=[
                    "order_number",
                    "user_username",
                    "user_email",
                    "status",
                    "amount_total",
                    "updated_at",
                ]
            )

        return SessionDTO.from_model(session)

    def get_session_by_token(self, token: uuid.UUID) -> Optional[dict]:
        try:
            session = PaymentSession.objects.prefetch_related("items").get(token=token)
            return SessionDTO.from_model(session)
        except PaymentSession.DoesNotExist:
            return None

    def get_completed_session(
        self, token: uuid.UUID, user_id: int
    ) -> SessionDTO | None:
        try:
            session = PaymentSession.objects.prefetch_related("items").get(
                token=token,
                user_id=user_id,
                status=PaymentSessionStatus.COMPLETED,
            )
            return SessionDTO.from_model(session)
        except PaymentSession.DoesNotExist:
            return None

    def get_pending_session_for_checkout(
        self, token: uuid.UUID, user_id: int
    ) -> SessionDTO | None:
        try:
            session = PaymentSession.objects.prefetch_related("items").get(
                token=token,
                user_id=user_id,
            )
            return SessionDTO.from_model(session)
        except PaymentSession.DoesNotExist:
            return None

    def invalidate_pending_sessions(self, order_id: int) -> int:
        return PaymentSession.objects.filter(
            order_id=order_id, status=PaymentSessionStatus.PENDING
        ).delete()[0]

    def complete_payment_session(self, token: uuid.UUID) -> SessionDTO | None:
        try:
            session = PaymentSession.objects.get(token=token)
            session.status = PaymentSessionStatus.COMPLETED
            session.completed_at = timezone.now()
            session.save(update_fields=["status", "completed_at", "updated_at"])
            return SessionDTO.from_model(session)
        except PaymentSession.DoesNotExist:
            return None
