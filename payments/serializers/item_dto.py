class ItemDTO:
    def __call__(self, item):
        return {
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "unit_price": item.unit_price,
            "quantity": item.quantity,
            "line_total": item.unit_price * item.quantity,
        }

    def __str__(self):
        return f"ItemDTO(id={self.id}, product_id={self.product_id}, product_name={self.product_name}, unit_price={self.unit_price}, quantity={self.quantity})"

    def __repr__(self):
        return self.__str__()
