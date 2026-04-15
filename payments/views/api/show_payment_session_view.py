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

