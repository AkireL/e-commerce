from dataclasses import dataclass, field


@dataclass
class ShowOrderInput:
    user_id: int


@dataclass
class ItemDisplayData:
    id: int
    product_id: int
    product_name: str
    product_price: str
    quantity: int
    line_total: str
    stock: int = 0
    photo_url: str | None = None

    @property
    def product(self) -> dict:
        return {
            "stock": self.stock,
            "photo_url": self.photo_url,
        }


@dataclass
class ShowOrderOutput:
    order_id: int | None
    items: list[ItemDisplayData] = field(default_factory=list)
    order_total: str = "0.00"
    is_active: bool = False


class ShowOrderUseCase:
    def __init__(self, order_repo, product_client):
        self.order_repo = order_repo
        self.product_client = product_client

    def execute(self, input: ShowOrderInput) -> ShowOrderOutput:
        order_entity = self.order_repo.get_active_order(input.user_id)
        if not order_entity:
            return ShowOrderOutput(order_id=None)

        product_ids = [item.product_id for item in order_entity.items]
        products = self.product_client.get_products_info(product_ids)

        items = []
        for item in order_entity.items:
            product_data = products.get(str(item.product_id)) or {}
            items.append(ItemDisplayData(
                id=item.id or 0,
                product_id=item.product_id,
                product_name=item.product_name,
                product_price=f"{item.product_price:.2f}",
                quantity=item.quantity,
                line_total=f"{item.line_total:.2f}",
                stock=product_data.get("stock", 0),
                photo_url=product_data.get("photo_url"),
            ))

        return ShowOrderOutput(
            order_id=order_entity.id,
            items=items,
            order_total=f"{order_entity.calculate_total():.2f}",
            is_active=order_entity.is_active,
        )
