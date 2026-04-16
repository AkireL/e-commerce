from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.serializers import OrderSerializer
from orders.repositories import OrderRepository
from logger.logger import logger


order_repository = OrderRepository()


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = order_repository.get_order_with_items(pk)
        
        if order is None or order.user_id != request.user.id:
            logger.warning(f"orders:api OrderDetailView - Order with id {pk} not found for user {request.user.id}.")
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        logger.warning(f"orders:api OrderDetailView - Order with id {pk} retrieved successfully for user {request.user.id}.")
        return Response({'order': serializer.data})


class OrderMarkPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_id = request.data.get('user_id')
        order = order_repository.get_order_by_id(pk)
        
        if order is None or order.user_id != user_id or not order.is_active:
            logger.warning(f"orders:api OrderMarkPaidView - Order with id {pk} not found or already marked as paid for user {user_id}.")
            return Response(
                {'success': False, 'error': 'Order not found or already paid'},
                status=status.HTTP_404_NOT_FOUND
            )

        order_repository.mark_as_paid(pk)
        
        logger.warning(f"orders:api OrderMarkPaidView - Order with id {pk} marked as paid for user {user_id}.")
        return Response({'success': True})