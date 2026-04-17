from typing import Optional

from products.models import Product


class ProductRepository:
    def get_all(self):
        return Product.objects.all()

    def get_by_id(self, pk: int) -> Optional[Product]:
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get_by_id_or_404(self, pk: int) -> Product:
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Product, pk=pk)

    def create(self, **data) -> Product:
        return Product.objects.create(**data)

    def update(self, pk: int, **data) -> Optional[Product]:
        product = self.get_by_id(pk)
        if product:
            for key, value in data.items():
                setattr(product, key, value)
            product.save()
        return product

    def delete(self, pk: int) -> bool:
        product = self.get_by_id(pk)
        if product:
            product.delete()
            return True
        return False

    def exists(self, pk: int) -> bool:
        return Product.objects.filter(pk=pk).exists()

    def filter(self, **kwargs):
        return Product.objects.filter(**kwargs)