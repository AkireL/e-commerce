import json
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.views.generic import FormView

from .exceptions import EmptyOrderError
from .forms import PaymentForm
from .http_client import mark_order_as_paid
from .services import (
    complete_payment_session,
    create_payment_session,
    get_pending_session_for_checkout,
)


@login_required
def create_session_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    order_id = request.POST.get("order_id")
    items_raw = request.POST.getlist("items")
    
    if not order_id or not items_raw:
        messages.error(request, "No se encontró información de la orden.")
        return redirect("my-orders")
    
    try:
        items = [json.loads(item) for item in items_raw]
    except json.JSONDecodeError:
        messages.error(request, "Error al procesar los productos.")
        return redirect("my-orders")
    
    if not items:
        messages.error(request, "La orden no tiene productos para pagar.")
        return redirect("my-orders")

    order_data = {
        "id": int(order_id),
        "items": items,
    }

    try:
        session_data = create_payment_session(order_data, request.user.id, request.user.username, request.user.email)
    except EmptyOrderError as exc:
        messages.error(request, str(exc))
        return redirect("my-orders")

    messages.info(request, "Redirigiéndote a la pasarela de pago simulada.")
    return redirect("payments:checkout", token=session_data['token'])


class PaymentCheckoutView(LoginRequiredMixin, FormView):
    template_name = "payments/checkout.html"
    form_class = PaymentForm

    def dispatch(self, request, *args, **kwargs):
        token_raw = kwargs.get("token")
        if token_raw is None:
            messages.error(request, "Token no proporcionado.")
            return redirect("my-orders")
        
        try:
            token = uuid.UUID(str(token_raw))
        except (ValueError, AttributeError):
            messages.error(request, "Token inválido.")
            return redirect("my-orders")
        
        self.session_data = get_pending_session_for_checkout(
            token, request.user.id, request.user.username, request.user.email
        )

        if self.session_data is None:
            messages.error(request, "Sesión de pago no encontrada.")
            return redirect("my-orders")

        if self.session_data.get('status') == "completed":
            messages.info(request, "Esta sesión ya fue procesada.")
            return redirect("order-processed", token=self.session_data.get('token'))

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
        return redirect("order-processed", token=self.session_data['token'])
