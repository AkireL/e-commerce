from dataclasses import dataclass
from decimal import Decimal


@dataclass
class UpdateItemInput:
    user_id: int
    item_id: int
    quantity: int


@dataclass
class UpdateItemOutput:
    success: bool
    message: str
    quantity: int = 0
    item_total: str = "0.00"
    order_total: str = "0.00"
    adjusted: bool = False
    removed: bool = False
    order_empty: bool = False
    available_stock: int = 0


def _format_amount(value: Decimal) -> str:
    if value is None:
        value = Decimal("0.00")
    return f"{value:.2f}"


class UpdateItemUseCase:
    def __init__(self, order_repo, product_client, payments_client):
        self.order_repo = order_repo
        self.product_client = product_client
        self.payments_client = payments_client

    def execute(self, input: UpdateItemInput) -> UpdateItemOutput:
        order = self.order_repo.get_active_order(input.user_id)
        if not order:
            return UpdateItemOutput(
                success=False,
                message="No tienes un carrito activo.",
            )

        item = next(
            (i for i in order.items if (i.id or 0) == input.item_id),
            None,
        )
        if not item:
            return UpdateItemOutput(
                success=False,
                message="El artículo seleccionado no existe en tu orden.",
            )

        stocks = self.product_client.get_products_stock([item.product_id])
        stock = stocks.get(str(item.product_id), 0)

        if stock is None or stock <= 0:
            order.remove_item(item.product_id)
            self.order_repo.save(order)
            self.payments_client.invalidate_payment_sessions(order.id or 0)

            return UpdateItemOutput(
                success=False,
                message="El producto ya no está disponible.",
                order_total=_format_amount(order.calculate_total()),
                order_empty=order.calculate_total() == Decimal("0.00"),
                removed=True,
            )

        adjusted = False
        quantity = input.quantity

        if quantity > stock:
            quantity = stock
            adjusted = True

        item.quantity = quantity
        self.order_repo.save(order)
        self.payments_client.invalidate_payment_sessions(order.id or 0)

        order_total = order.calculate_total()

        return UpdateItemOutput(
            success=True,
            message="Actualizado.",
            quantity=item.quantity,
            item_total=_format_amount(item.line_total),
            order_total=_format_amount(order_total),
            adjusted=adjusted,
            removed=False,
            order_empty=order_total == Decimal("0.00"),
            available_stock=stock,
        )
