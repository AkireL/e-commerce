from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from orders.forms import OrderProductForm
from orders.http_client import get_products_available
from orders.repositories import OrderRepository, OrderItemRepository


order_repository = OrderRepository()
order_item_repository = OrderItemRepository()


class CreateOrderProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = OrderProductForm(request.data, products=get_products_available())
        
        if not form.is_valid():
            errors = list(form.errors.values())
            return Response({
                'success': False,
                'message': errors[0][0] if errors else 'Formulario inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        quantity = form.cleaned_data["quantity"]
        product_id = int(form.cleaned_data["product"])
        product_data = form.get_product_data(product_id)
        
        user = request.user

        if not product_data:
            return Response({
                'success': False,
                'message': 'Producto no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

        order = order_repository.create_or_get_active(
            user.id,
            user.username,
            user.email,
        )
        
        order = order_repository.create_or_get_active(
            user.id,
            user.username,
            user.email,
        )

        item, created = order_item_repository.add_or_update_item(
            order,
            product_id,
            product_data['name'],
            product_data['price'],
            quantity,
        )

        return Response({
            'success': True,
            'message': f'El producto "{product_data["name"]}" se ha agregado al carrito',
            'quantity': item.quantity
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)