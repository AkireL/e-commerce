from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView


class ShowMyOrdersView(LoginRequiredMixin, DetailView):
    model = None
    template_name = 'my_orders.html'
    context_object_name = "order"
    show_order_service = None
    
    def __init__(self, show_order_service, **kwargs):
        super().__init__(**kwargs)
        self.show_order_service = show_order_service

    def get_object(self):
        return self.show_order_service.get_order(self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context.get("order")

        if order :
            service_data = self.show_order_service.get_items(order)    
            context.update(service_data)
        else :
            context.update(
                {
                    "order_items": [],
                    "order_total": Decimal("0.00"),
                 }) 

        context.setdefault("order_items", [])
        context.setdefault("order_total", Decimal("0.00"))

        return context