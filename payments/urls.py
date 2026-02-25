from django.urls import path

from .views import PaymentCheckoutView, create_session_view
from .api import get_completed_session_view, invalidate_sessions_view


app_name = "payments"

urlpatterns = [
    path("create-session/", create_session_view, name="create-session"),
    path("checkout/<uuid:token>/", PaymentCheckoutView.as_view(), name="checkout"),
    path("api/get-completed-session/<uuid:token>/", get_completed_session_view, name='api-get-completed-session'),
    path("api/invalidate-sessions/", invalidate_sessions_view, name='api-invalidate-sessions'),
]
