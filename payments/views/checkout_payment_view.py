import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import FormView

from payments.forms import PaymentForm
from logger.logger import logger


class PaymentCheckoutView(LoginRequiredMixin, FormView):
    template_name = "payments/checkout.html"
    form_class = PaymentForm
    payment_service = None

    def __init__(self, payment_service=None, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = payment_service

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
        
        session, was_completed = self.payment_service.get_active_session(str(token), request.user)

        logger.warning(f"checkout_payment_view - User {request.user.id} is trying to access payment session with token {token}.")
        logger.warning(f"checkout_payment_view - Session data: {session}, was_completed: {was_completed}")
        if session is None:
            messages.error(request, "Sesión no encontrada.")
            return redirect("orders:my-orders")
        
        if was_completed:
            messages.info(request, "Esta sesión ya fue procesada.")
            return redirect("orders:order-processed", token=token)
        
        self.session_data = session
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "session": self.session_data,
            }
        )
        return context

    def form_valid(self, form):
        user_id = self.request.user.id
        logger.warning(f"checkout_payment_view - form_valid: Processing payment for user_id: {user_id}, session_token: {self.session_data.token}")
        self.payment_service.checkout_session(self.session_data, user_id)
        
        messages.success(self.request, "Pago completado. ¡Gracias por tu compra!")
        return redirect("orders:order-processed", token=self.session_data.token)
