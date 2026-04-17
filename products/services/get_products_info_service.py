from products.serializers import ProductInfoSerializer


class GetProductsInfoService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def get_products_info(self, product_ids, request=None):
        if not isinstance(product_ids, list):
            return None

        products = self.product_repository.filter(id__in=product_ids)
        serializer = ProductInfoSerializer(products, many=True, context={'request': request})

        return {str(item['id']): item for item in serializer.data}