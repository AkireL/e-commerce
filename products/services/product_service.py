from typing import Optional

from products.models import Product


def get_product_by_id(product_id: int) -> Optional[dict]:
    try:
        product = Product.objects.get(pk=product_id)
        return {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'stock': product.stock,
            'available': product.available,
        }
    except Product.DoesNotExist:
        return None


def get_products_by_ids(product_ids: list[int]) -> dict[int, dict]:
    if not product_ids:
        return {}
    
    products = Product.objects.filter(id__in=product_ids)
    return {
        p.id: {
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'stock': p.stock,
            'available': p.available,
        }
        for p in products
    }
