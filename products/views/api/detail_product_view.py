from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ProductsInfoView(APIView):
    permission_classes = [IsAuthenticated]
    get_products_info_service = None

    def __init__(self, get_products_info_service=None, **kwargs):
        super().__init__(**kwargs)
        self.get_products_info_service = get_products_info_service

    def post(self, request):
        product_ids = request.data.get('product_ids', [])

        if not isinstance(product_ids, list):
            return Response({'error': 'product_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        result = self.get_products_info_service.get_products_info(product_ids, request)
        return Response({'products': result})