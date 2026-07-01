from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class OrderItemEntity:
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int
    id: int | None = None

    @property
    def line_total(self) -> Decimal:
        return self.product_price * self.quantity


@dataclass
class OrderEntity:
    user_id: int
    user_username: str
    user_email: str
    is_active: bool = True
    id: int | None = None
    items: list[OrderItemEntity] = field(default_factory=list)

    def add_item(self, item: OrderItemEntity) -> tuple["OrderItemEntity", bool]:
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                return existing, False
        self.items.append(item)
        return item, True

    def remove_item(self, product_id: int) -> OrderItemEntity | None:
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                return self.items.pop(i)
        return None

    def calculate_total(self) -> Decimal:
        return sum((item.line_total for item in self.items), Decimal("0.00"))
