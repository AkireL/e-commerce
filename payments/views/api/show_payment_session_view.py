from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from payments.services.payment_service import PaymentService

class PaymentSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    payment_service = PaymentService()
    
    def get(self, request, token):
        try:
            session = self.payment_service.get_completed_session(token, request.user.id)        
            return Response({'session': session})
        except Exception:
            return Response({'session': None})


