from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.serializers import OrderSerializer
from orders.use_cases.order_detail import OrderDetailInput
from orders.use_cases.paid_order import PaidOrderInput
from logger.logger import logger


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    use_case = None

    def __init__(self, use_case=None, **kwargs):
        super().__init__(**kwargs)
        self.use_case = use_case

    def get(self, request, pk):
        input = OrderDetailInput(
            order_id=pk,
            user_id=request.user.id,
        )
        result = self.use_case.execute(input)

        if not result.success:
            logger.warning(f"orders:api OrderDetailView - Order with id {pk} not found for user {request.user.id}.")
            return Response({'error': result.error}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(result.order)
        logger.warning(f"orders:api OrderDetailView - Order with id {pk} retrieved successfully for user {request.user.id}.")
        return Response({'order': serializer.data})


class OrderMarkPaidView(APIView):
    permission_classes = [IsAuthenticated]
    use_case = None

    def __init__(self, use_case=None, **kwargs):
        super().__init__(**kwargs)
        self.use_case = use_case

    def post(self, request, pk):
        input = PaidOrderInput(
            order_id=pk,
            user_id=request.user.id,
        )

        result = self.use_case.execute(input)

        if not result.success:
            return Response({'error': result.error}, status=status.HTTP_404_NOT_FOUND)

        return Response({'success': True})
