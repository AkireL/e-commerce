from dataclasses import dataclass, field


@dataclass
class ShowProcessedOrderInput:
    token: str
    user_id: int


@dataclass
class ProcessedItemData:
    product_id: int
    product_name: str
    unit_price: str
    quantity: int
    line_total: str


@dataclass
class ShowProcessedOrderOutput:
    success: bool
    token: str = ""
    order_id: int = 0
    user_id: int = 0
    items: list[ProcessedItemData] = field(default_factory=list)
    amount_total: str = "0.00"


class ShowProcessedOrderUseCase:
    def __init__(self, payments_client):
        self.payments_client = payments_client

    def execute(self, input: ShowProcessedOrderInput) -> ShowProcessedOrderOutput:
        session = self.payments_client.get_payment_completed_session(
            input.token
        )

        if not session:
            return ShowProcessedOrderOutput(success=False)

        items = [
            ProcessedItemData(
                product_id=item.get("product_id"),
                product_name=item.get("product_name"),
                unit_price=str(item.get("unit_price", "0.00")),
                quantity=item.get("quantity", 0),
                line_total=str(item.get("line_total", "0.00")),
            )
            for item in session.get("items", [])
        ]

        return ShowProcessedOrderOutput(
            success=True,
            token=str(session.get("token", "")),
            order_id=session.get("order_id", 0),
            user_id=session.get("user_id", 0),
            items=items,
            amount_total=str(session.get("amount_total", "0.00")),
        )
