class CreateProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def create(self, data):
        return self.product_repository.create(**data)