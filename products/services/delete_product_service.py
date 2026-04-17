class DeleteProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def delete(self, pk: int):
        return self.product_repository.delete(pk)

    def exists(self, pk: int) -> bool:
        return self.product_repository.exists(pk)