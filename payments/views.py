from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import FormView

from orders.models import Order

from .exceptions import EmptyOrderError
from .forms import PaymentForm
from .models import PaymentSession, PaymentSessionStatus
from .services import create_payment_session


@login_required
def create_session_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    order = (
        Order.objects
        .prefetch_related("orderproduct_set__product")
        .filter(user_id=request.user.id, is_active=True, )
        .first()
    )

    if not order:
        messages.error(request, "No se encontró una orden activa para procesar.")
        return redirect("my-orders")

    try:
        session = create_payment_session(order, request.user)
    except EmptyOrderError as exc:
        messages.error(request, str(exc))
        return redirect("my-orders")

    messages.info(request, "Redirigiéndote a la pasarela de pago simulada.")
    return redirect(session.get_checkout_url())


class PaymentCheckoutView(LoginRequiredMixin, FormView):
    template_name = "payments/checkout.html"
    form_class = PaymentForm

    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get("token")
        self.session = get_object_or_404(
            PaymentSession.objects.select_related("order", "user").prefetch_related("items"),
            token=token,
            user=request.user,
        )

        if self.session.status == PaymentSessionStatus.COMPLETED:
            messages.info(request, "Esta sesión ya fue procesada.")
            return redirect("order-processed", token=self.session.token)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "session": self.session,
                "items": self.session.items.all(),
            }
        )
        return context

    def form_valid(self, form):
        self.session.status = PaymentSessionStatus.COMPLETED
        self.session.completed_at = timezone.now()
        self.session.save(update_fields=["status", "completed_at", "updated_at"])

        # TODO: Esta logica no debe ir aqui porque es parte del dominio del orders, hay que crear un servicio en orders para marcar la orden como pagada
        order = self.session.order
        if order.is_active:
            order.is_active = False
            order.save(update_fields=["is_active"])

        messages.success(self.request, "Pago completado. ¡Gracias por tu compra!")
        
        # TODO: Usar el id de la orden en vez del token porque en el modulo orders solo conoce el id.
        return redirect("order-processed", token=self.session.token)
