from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView

from payments.models import PaymentSession, PaymentSessionStatus

from .forms import OrderProductForm
from .models import Order

class MyOrdersView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'my_orders.html'
    context_object_name = "order"

    def get_object(self):
        return Order.objects.filter(is_active=True, user=self.request.user).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context.get("order")

        if order:
            items = list(order.orderproduct_set.select_related("product"))
            total = sum((item.product.price * item.quantity for item in items), Decimal("0.00"))
            context.update(
                {
                    "order_items": items,
                    "order_total": total,
                }
            )

        context.setdefault("order_items", [])
        context.setdefault("order_total", Decimal("0.00"))

        return context
    
class CreateOrderProductView(LoginRequiredMixin, CreateView):
    template_name="create_order_product.html"
    form_class = OrderProductForm
    success_url = reverse_lazy('my-orders')

    def form_valid(self, form):
        order, _ = Order.objects.get_or_create(
            is_active=True,
            user=self.request.user
        )

        quantity = form.cleaned_data["quantity"]
        product = form.cleaned_data["product"]
        
        order_product, created = order.orderproduct_set.get_or_create(
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            order.orderproduct_set.filter(pk=order_product.pk).update(quantity=quantity)
            order_product.refresh_from_db(fields=["quantity"])

        self.object = order_product
        return HttpResponseRedirect(self.get_success_url())


class OrderProcessedView(LoginRequiredMixin, TemplateView):
    template_name = "order_processed.html"

    def dispatch(self, request, *args, **kwargs):
        # TODO: payments debe devolver el id de la orden y no el token de la sesion de pago porque el modulo orders no debe conocer nada del modulo payments, lo ideal es que el modulo orders tenga un servicio para obtener la orden por token y el modulo payments solo conozca ese servicio.
        token = kwargs.get("token")
        self.session = self._get_session(token)
        return super().dispatch(request, *args, **kwargs)

    def _get_session(self, token):
        # TODO: hay que separar los dominios porque el modulo de payments no debe conocer nada del modulo de orders, lo ideal es que el modulo de orders tenga un servicio para obtener la orden por token y el modulo de payments solo conozca ese servicio.
        return get_object_or_404(
            self._session_queryset(),
            token=token,
            user=self.request.user,
            status=PaymentSessionStatus.COMPLETED,
        )

    
    def _session_queryset(self):
        return PaymentSession.objects.select_related("order", "user").prefetch_related("items")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.session.order
        items = self.session.items.all()
        context.update(
            {
                "session": self.session,
                "order": order,
                "items": items,
            }
        )
        return context
