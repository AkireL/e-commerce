from django.urls import path

from payments.clients.order_client import order_client
from payments.views.checkout_payment_view import PaymentCheckoutView
from payments.views.create_session_view import CreateSessionView
from payments.views.api.show_payment_session_view import PaymentSessionDetailView
from payments.views.api.invalidate_sessions_view import InvalidateSessionsView

from payments.services.payment_service import PaymentService
from payments.repositories.payment_session_repository import PaymentSessionRepository
from payments.repositories.payment_items_repository import PaymentItemRepository

app_name = "payments"

payment_service_instance = PaymentService(
    session_repository=PaymentSessionRepository(
        payment_item_repository=PaymentItemRepository()
    ),
    order_client=order_client,
)

urlpatterns = [
    path(
        "create-session/",
        CreateSessionView.as_view(payment_service=payment_service_instance),
        name="create-session",
    ),
    path(
        "checkout/<uuid:token>/",
        PaymentCheckoutView.as_view(payment_service=payment_service_instance),
        name="checkout",
    ),
    path(
        "sessions/<uuid:token>/",
        PaymentSessionDetailView.as_view(payment_service=payment_service_instance),
        name="api-session-detail",
    ),
    path(
        "sessions/invalidate/",
        InvalidateSessionsView.as_view(payment_service=payment_service_instance),
        name="api-invalidate-sessions",
    ),
]
