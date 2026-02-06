from django.shortcuts import render
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
        form.instance.order = order
        form.instance.quantity = 1
        form.save()

        return super().form_valid(form)