from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from logger.logger import logger

class PaymentSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    payment_service = None

    def __init__(self, payment_service=None, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = payment_service

    def get(self, request, token):
        try:
            session = self.payment_service.get_completed_session(token)      
            return Response({'session': session.toJson()})
        except Exception as e:
            return Response({'session': None})


