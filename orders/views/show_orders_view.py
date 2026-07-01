from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from orders.use_cases.show_order import ShowOrderInput


class ShowMyOrdersView(LoginRequiredMixin, TemplateView):
    template_name = "my_orders.html"
    use_case = None

    def __init__(self, use_case=None, **kwargs):
        super().__init__(**kwargs)
        self.use_case = use_case

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        input = ShowOrderInput(user_id=self.request.user.id)
        result = self.use_case.execute(input)

        context["order"] = {
            "id": result.order_id,
            "is_active": result.is_active,
        } if result.order_id else None
        context["order_items"] = result.items
        context["order_total"] = result.order_total

        return context
