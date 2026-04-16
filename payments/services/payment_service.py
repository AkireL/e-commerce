from payments.repositories.payment_session_repository import PaymentSessionRepository
from payments.clients.order_client import order_client

class PaymentService:
    session_repository = PaymentSessionRepository()

    def get_active_session(self, token, user):
        session = self.session_repository.get_pending_session_for_checkout(
            token, user.id, user.username, user.email
        )

        if session is None:
            return None, False
        
        if session.status == "completed":
            return session, True
        
        return session, False

    def checkout_session(self, session, user_id):
        self.session_repository.complete_payment_session(session.token)
        order_client.mark_order_as_paid(session.order_id, user_id)

    def create_payment_session(self, user, order_data):
        return self.session_repository.create_payment_session(order_data, user)
    
    def get_completed_session(self, token, user):
        return self.session_repository.get_completed_session(token, user.id)

    def invalidate_pending_sessions(self, order_id):
        return self.session_repository.invalidate_pending_sessions(order_id)