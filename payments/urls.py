from django.urls import path

from .views import PaymentCheckoutView, create_session_view
from .api import PaymentSessionDetailView, InvalidateSessionsView


app_name = "payments"

urlpatterns = [
    path("create-session/", create_session_view, name="create-session"),
    path("checkout/<uuid:token>/", PaymentCheckoutView.as_view(), name="checkout"),
    path("api/sessions/<uuid:token>/", PaymentSessionDetailView.as_view(), name='api-session-detail'),
    path("api/sessions/invalidate/", InvalidateSessionsView.as_view(), name='api-invalidate-sessions'),
]
