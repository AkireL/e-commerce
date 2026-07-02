from dataclasses import dataclass


@dataclass
class PaidOrderInput:
    order_id: int


@dataclass
class PaidOrderOutput:
    success: bool
    error: str | None = None


class PaidOrderUseCase:
    def __init__(self, order_repo):
        self.order_repo = order_repo

    def execute(self, input: PaidOrderInput) -> PaidOrderOutput:
        order = self.order_repo.get_by_id(input.order_id)

        if order is None:
            return PaidOrderOutput(success=False, error="Order not found")
        
        if not order.is_active:
            return PaidOrderOutput(success=False, error="Order already paid")

        order.is_active = False
        self.order_repo.save(order)

        return PaidOrderOutput(success=True)
