from orders.use_cases.order_detail import IOrderDetailPresenter, OrderDetailOutput


class OrderDetailPresenter:
    def present_order(self, order) -> OrderDetailOutput:
        return OrderDetailOutput(success=True, order=order)

    def present_error(self, error: str) -> OrderDetailOutput:
        return OrderDetailOutput(success=False, error=error)
