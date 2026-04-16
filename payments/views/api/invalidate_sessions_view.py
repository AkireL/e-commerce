from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class InvalidateSessionsView(APIView):
    permission_classes = [IsAuthenticated]
    payment_service = None

    def __init__(self, payment_service=None, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = payment_service

    def post(self, request):
        order_id = request.data.get('order_id')

        if not order_id:
            return Response({'error': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)

        deleted = self.payment_service.invalidate_pending_sessions(order_id)

        return Response({'deleted': deleted})
