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
        logger.warning(f"show_payment_session - User {request.user.id} is trying to access payment session with token {token}.")
        try:
            session = self.payment_service.get_completed_session(token, request.user.id)        
            return Response({'session': session})
        except Exception:
            return Response({'session': None})


