from dataclasses import dataclass


@dataclass
class OrderDetailInput:
    order_id: int
    user_id: int


@dataclass
class OrderDetailOutput:
    success: bool
    error: str | None = None
    order = None


class OrderDetailUseCase:
    def __init__(self, order_repo):
        self.order_repo = order_repo

    def execute(self, input: OrderDetailInput) -> OrderDetailOutput:
        order = self.order_repo.get_order_with_items(input.order_id)
        if order is None:
            return OrderDetailOutput(success=False, error="Order not found")
        if order.user_id != input.user_id:
            return OrderDetailOutput(success=False, error="Order not found")
        return OrderDetailOutput(success=True, order=order)
