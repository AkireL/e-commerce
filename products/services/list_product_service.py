from products.models import Product


class ListProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def get_products(self):
        return self.product_repository.get_all()

    def get_permissions(self, user):
        can = user.is_admin_or_editor()
        return {
            'products': {
                'edit': can,
                'create': can,
                'delete': can,
            }
        }