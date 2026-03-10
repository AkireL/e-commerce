from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.serializers import OrderSerializer


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.prefetch_related('items').get(pk=pk, user_id=request.user.id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response({'order': serializer.data})


class OrderMarkPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            user_id = request.data.get('user_id')
            order = Order.objects.get(pk=pk, user_id=user_id, is_active=True)
        except Order.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Order not found or already paid'},
                status=status.HTTP_404_NOT_FOUND
            )

        order.is_active = False
        order.save(update_fields=['is_active'])

        return Response({'success': True})
