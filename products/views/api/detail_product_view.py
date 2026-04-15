from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from products.models import Product
from products.serializers import (
    ProductInfoSerializer,
)

class ProductsInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_ids = request.data.get('product_ids', [])

        if not isinstance(product_ids, list):
            return Response({'error': 'product_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(id__in=product_ids)
        serializer = ProductInfoSerializer(products, many=True, context={'request': request})

        result = {str(item['id']): item for item in serializer.data}
        return Response({'products': result})
