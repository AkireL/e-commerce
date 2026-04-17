from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from orders.forms import OrderProductForm
from orders.http_client import get_products_available


class CreateOrderProductView(APIView):
    permission_classes = [IsAuthenticated]
    add_product_service = None

    def __init__(self, add_product_service, **kwargs):
        super().__init__(**kwargs)
        self.add_product_service = add_product_service

    def post(self, request):
        form = OrderProductForm(request.data, products=get_products_available())

        if not form.is_valid():
            errors = list(form.errors.values())
            return Response(
                {
                    "success": False,
                    "message": errors[0][0] if errors else "Formulario inválido",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantity = form.cleaned_data["quantity"]
        product_id = int(form.cleaned_data["product"])
        product_data = form.get_product_data(product_id)

        user = request.user

        if not product_data:
            return Response(
                {"success": False, "message": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        response = self.add_product_service.execute(
            user=user,
            new_item={
                "product_id": product_id,
                "product_name": product_data["name"],
                "product_price": product_data["price"],
                "quantity": quantity,
            },
        )

        return Response(
            {
                "success": True,
                "message": f'El producto "{product_data["name"]}" se ha agregado al carrito',
                "quantity": response["quantity"],
            },
            status=(
                status.HTTP_201_CREATED if response["created"] else status.HTTP_200_OK
            ),
        )
