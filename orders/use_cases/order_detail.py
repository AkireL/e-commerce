from dataclasses import dataclass
from typing import Protocol
from logger.logger import logger


@dataclass
class OrderDetailInput:
    order_id: int
    user_id: int


@dataclass
class OrderDetailOutput:
    success: bool
    error: str | None = None
    order = None


class IOrderDetailPresenter(Protocol):
    def present_order(self, order) -> OrderDetailOutput: ...

    def present_error(self, error: str) -> OrderDetailOutput: ...


class OrderDetailUseCase:
    def __init__(self, order_repo, presenter: IOrderDetailPresenter):
        self.order_repo = order_repo
        self.presenter = presenter

    def execute(self, input: OrderDetailInput) -> OrderDetailOutput:
        order = self.order_repo.get_order_with_items(input.order_id)
        if order is None:
            return self.presenter.present_error("Order not found")
        if order.user_id != input.user_id:
            return self.presenter.present_error("Order not found")
        return self.presenter.present_order(order)
