from payments.serializers.item_dto import ItemDTO
from payments.models import PaymentItem, PaymentSession


class SessionDTO:

    def __init__(
        self,
        id,
        token,
        order_id,
        order_number,
        user_id,
        user_username,
        user_email,
        status,
        amount_total,
        items,
        get_checkout_url,
    ):
        self.id = id
        self.token = token
        self.order_id = order_id
        self.order_number = order_number
        self.user_id = user_id
        self.user_username = user_username
        self.user_email = user_email
        self.status = status
        self.amount_total = amount_total
        self.items = items
        self.get_checkout_url = get_checkout_url

    @staticmethod
    def from_model(
        session: PaymentSession, items: list[PaymentItem] | None = None
    ) -> "SessionDTO":
        if items is None:
            items = list(session.items.all())

        item_dto = ItemDTO()

        return SessionDTO(
            id=session.id,
            token=session.token,
            order_id=session.order_id,
            order_number=session.order_number,
            user_id=session.user_id,
            user_username=session.user_username,
            user_email=session.user_email,
            status=session.status,
            amount_total=session.amount_total,
            items=[item_dto(item) for item in items],
            get_checkout_url=f"/payments/checkout/{session.token}/",
        )

    def __str__(self) -> str:
        return f"SessionDTO(id={self.id}, token={self.token}, order_number={self.order_number}, status={self.status}, amount_total={self.amount_total}, items={len(self.items)})"
