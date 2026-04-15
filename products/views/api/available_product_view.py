from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from products.models import Product
from products.serializers import ProductListSerializer

class ProductsAvailableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(available=True)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response({'products': serializer.data})

