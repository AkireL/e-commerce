from django.urls import path

from payments.views.checkout_payment_view import PaymentCheckoutView
from payments.views.create_session_view import create_session_view
from payments.views.api.show_payment_session_view import PaymentSessionDetailView
from payments.views.api.invalidate_sessions_view import InvalidateSessionsView

app_name = "payments"

urlpatterns = [
    path("create-session/", create_session_view, name="create-session"),
    path("checkout/<uuid:token>/", PaymentCheckoutView.as_view(), name="checkout"),
    path("sessions/<uuid:token>/", PaymentSessionDetailView.as_view(), name='api-session-detail'),
    path("sessions/invalidate/", InvalidateSessionsView.as_view(), name='api-invalidate-sessions'),
]
