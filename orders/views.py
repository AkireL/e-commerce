from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Order
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import OrderProductForm
from django.urls import reverse_lazy

class MyOrdersView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'my_orders.html'
    context_object_name = "order"

    def get_object(self):
        return Order.objects.filter(is_active=True, user=self.request.user).first()
    
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
