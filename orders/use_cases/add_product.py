from dataclasses import dataclass
from decimal import Decimal

from orders.domain.entities import OrderEntity, OrderItemEntity


@dataclass
class AddProductInput:
    user_id: int
    user_username: str
    user_email: str
    product_id: int
    quantity: int


@dataclass
class AddProductOutput:
    success: bool
    message: str
    quantity: int = 0
    created: bool = False


class AddProductUseCase:
    def __init__(self, order_repo, product_client):
        self.order_repo = order_repo
        self.product_client = product_client

    def execute(self, input: AddProductInput) -> AddProductOutput:
        product = self.product_client.get_product_info(input.product_id)
        if not product:
            return AddProductOutput(success=False, message="Producto no encontrado")

        order = self.order_repo.get_active_order(input.user_id)
        if not order:
            order = OrderEntity(
                user_id=input.user_id,
                user_username=input.user_username,
                user_email=input.user_email,
            )

        item, created = order.add_item(OrderItemEntity(
            product_id=input.product_id,
            product_name=str(product["name"]),
            product_price=Decimal(str(product["price"])),
            quantity=input.quantity,
        ))

        self.order_repo.save(order)

        return AddProductOutput(
            success=True,
            message=f'El producto "{product["name"]}" se ha agregado al carrito',
            quantity=item.quantity,
            created=created,
        )
