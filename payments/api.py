from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from payments.models import PaymentSession, PaymentSessionStatus
from payments.serializers import PaymentSessionSerializer


class PaymentSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, token):
        try:
            session = PaymentSession.objects.prefetch_related('items').get(
                token=token,
                user_id=request.user.id,
                status=PaymentSessionStatus.COMPLETED,
            )
        except PaymentSession.DoesNotExist:
            return Response({'session': None})

        serializer = PaymentSessionSerializer(session)
        return Response({'session': serializer.data})


class InvalidateSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')

        if not order_id:
            return Response({'error': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)

        deleted = PaymentSession.objects.filter(
            order_id=order_id,
            status=PaymentSessionStatus.PENDING
        ).delete()[0]

        return Response({'deleted': deleted})
