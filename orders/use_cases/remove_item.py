from dataclasses import dataclass
from decimal import Decimal


@dataclass
class RemoveItemInput:
    user_id: int
    item_id: int


@dataclass
class RemoveItemOutput:
    success: bool
    message: str
    order_total: str = "0.00"
    order_empty: bool = False


def _format_amount(value: Decimal) -> str:
    if value is None:
        value = Decimal("0.00")
    return f"{value:.2f}"


class RemoveItemUseCase:
    def __init__(self, order_repo, payments_client):
        self.order_repo = order_repo
        self.payments_client = payments_client

    def execute(self, input: RemoveItemInput) -> RemoveItemOutput:
        order = self.order_repo.get_active_order(input.user_id)
        if not order:
            return RemoveItemOutput(
                success=False,
                message="No tienes un carrito activo.",
            )

        removed = order.remove_item(input.item_id)
        if not removed:
            return RemoveItemOutput(
                success=False,
                message="El artículo que intentas eliminar no existe.",
            )

        product_name = removed.product_name
        self.order_repo.save(order)
        self.payments_client.invalidate_payment_sessions(order.id or 0)

        order_total = order.calculate_total()
        order_empty = order_total == Decimal("0.00")

        return RemoveItemOutput(
            success=True,
            message=f"{product_name} fue eliminado del carrito.",
            order_total=_format_amount(order_total),
            order_empty=order_empty,
        )
