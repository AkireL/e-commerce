from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.use_cases.paid_order import PaidOrderInput
from logger.logger import logger


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.prefetch_related("items").get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.user_id != request.user.id:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response({'order': serializer.data})


class OrderMarkPaidView(APIView):
    permission_classes = [IsAuthenticated]
    use_case = None

    def __init__(self, use_case=None, **kwargs):
        super().__init__(**kwargs)
        self.use_case = use_case

    def post(self, request, pk):
        owner_id= request.data.get('owner_id', None)

        input = PaidOrderInput(
            order_id=pk,
            user_id=owner_id,
        )
        result = self.use_case.execute(input)

        if not result.success:
            return Response({'error': result.error}, status=status.HTTP_404_NOT_FOUND)

        return Response({'success': True})
