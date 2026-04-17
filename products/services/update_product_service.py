class UpdateProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def update(self, pk: int, data):
        return self.product_repository.update(pk, **data)

    def get_product(self, pk: int):
        return self.product_repository.get_by_id(pk)