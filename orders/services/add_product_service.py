from django.contrib.auth.models import User

class AddProductService:

    def __init__(self, order_repository, order_item_repository):
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository

    def execute(self, user: User, new_item: dict):
        order = self.order_repository.create_or_get_active(
            user.id,
            user.username,
            user.email,
        )
        
        order = self.order_repository.create_or_get_active(
            user.id,
            user.username,
            user.email,
        )

        item, created = self.order_item_repository.add_or_update_item(
            order,
            new_item["product_id"],
            new_item["product_name"],
            new_item["product_price"],
            new_item["quantity"],
        )

        return {
            'success': True,
            'created': created,
            'message': f'El producto "{new_item["product_name"]}" se ha agregado al carrito',
            'quantity': item.quantity
        }