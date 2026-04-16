class PaymentService:
    def __init__(self, session_repository, order_client):
        self.session_repository = session_repository
        self._order_client = order_client

    def get_active_session(self, token, user):
        session = self.session_repository.get_pending_session_for_checkout(
            token, user.id
        )

        if session is None:
            return None, False

        if session.status == "completed":
            return session, True

        return session, False

    def checkout_session(self, session, user_id):
        self.session_repository.complete_payment_session(session.token)
        self._order_client.mark_order_as_paid(session.order_id, user_id)

    def create_payment_session(self, user, order_data):
        return self.session_repository.create_payment_session(order_data, user)

    def get_completed_session(self, token, user):
        return self.session_repository.get_completed_session(token, user.id)

    def invalidate_pending_sessions(self, order_id):
        return self.session_repository.invalidate_pending_sessions(order_id)
