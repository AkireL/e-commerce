from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from orders.forms import OrderProductForm
from orders.use_cases.add_product import AddProductInput


class CreateOrderProductView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, use_case=None, **kwargs):
        super().__init__(**kwargs)
        self.use_case = use_case

    def post(self, request):
        form = OrderProductForm(request.data)

        if not form.is_valid():
            errors = list(form.errors.values())
            return Response(
                {
                    "success": False,
                    "message": errors[0][0] if errors else "Formulario inválido",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        input = AddProductInput(
            user_id=request.user.id,
            user_username=request.user.username,
            user_email=request.user.email,
            product_id=form.cleaned_data["product"],
            quantity=form.cleaned_data["quantity"],
        )

        result = self.use_case.execute(input)

        return Response(
            {
                "success": result.success,
                "message": result.message,
                "quantity": result.quantity,
            },
            status=status.HTTP_201_CREATED if result.created else status.HTTP_200_OK,
        )
