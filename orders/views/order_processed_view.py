import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView


class OrderProcessedView(LoginRequiredMixin, TemplateView):
    template_name = "order_processed.html"
    payments_client = None

    def __init__(self, payments_client=None, **kwargs):
        super().__init__(**kwargs)
        self.payments_client = payments_client

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
        
        self.session_data = self.payments_client.get_payment_completed_session(str(token), request.user.id)
        
        if self.session_data is None:
            return redirect("orders:my-orders")
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update(
            {
                "session": self.session_data,
                "order": self.session_data.get("order_id"),
                "items": self.session_data.get("items", []),
            }
        )
        return context