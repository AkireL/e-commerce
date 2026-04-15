from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from orders.forms import OrderProductForm
from orders.http_client import (
    get_products_available,
)
from orders.models import Order

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

        order, _ = Order.objects.get_or_create(
            is_active=True,
            user_id=request.user.id,
        )

        quantity = form.cleaned_data["quantity"]
        product_id = int(form.cleaned_data["product"])
        product_data = form.get_product_data(product_id)

        if not product_data:
            return Response({
                'success': False,
                'message': 'Producto no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

        order_product, created = order.items.get_or_create(
            product_id=product_id,
            product_name=product_data['name'],
            product_price=product_data['price'],
            defaults={"quantity": quantity}
        )

        if not created:
            order.items.filter(pk=order_product.pk).update(quantity=quantity)
            order_product.refresh_from_db(fields=["quantity"])

        return Response({
            'success': True,
            'message': f'El producto "{product_data["name"]}" se ha agregado al carrito',
            'quantity': order_product.quantity
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
