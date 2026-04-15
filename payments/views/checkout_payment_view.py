import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import FormView

from payments.forms import PaymentForm
from payments.http_client import mark_order_as_paid
from payments.services import (
    complete_payment_session,
    get_pending_session_for_checkout,
)

class PaymentCheckoutView(LoginRequiredMixin, FormView):
    template_name = "payments/checkout.html"
    form_class = PaymentForm

    def dispatch(self, request, *args, **kwargs):
        token_raw = kwargs.get("token")
        if token_raw is None:
            messages.error(request, "Token no proporcionado.")
            return redirect("orders:my-orders")
        
        try:
            token = uuid.UUID(str(token_raw))
        except (ValueError, AttributeError):
            messages.error(request, "Token inválido.")
            return redirect("orders:my-orders")
        
        self.session_data = get_pending_session_for_checkout(
            token, request.user.id, request.user.username, request.user.email
        )

        if self.session_data is None:
            messages.error(request, "Sesión de pago no encontrada.")
            return redirect("my-orders")

        if self.session_data.get('status') == "completed":
            messages.info(request, "Esta sesión ya fue procesada.")
            return redirect("orders:order-processed", token=self.session_data.get('token'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "session": self.session_data,
                "items": self.session_data.get('items', []),
            }
        )
        return context

    def form_valid(self, form):
        user_id = self.request.user.id
        complete_payment_session(self.session_data['token'])
        mark_order_as_paid(self.session_data['order_id'], user_id)

        messages.success(self.request, "Pago completado. ¡Gracias por tu compra!")
        return redirect("orders:order-processed", token=self.session_data['token'])
