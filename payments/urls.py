from django.urls import path

from .views import PaymentCheckoutView, create_session_view


app_name = "payments"

urlpatterns = [
    path("create-session/", create_session_view, name="create-session"),
    path("checkout/<uuid:token>/", PaymentCheckoutView.as_view(), name="checkout"),
]
