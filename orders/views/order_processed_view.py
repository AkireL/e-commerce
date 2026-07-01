import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from orders.use_cases.show_processed_order import ShowProcessedOrderInput


class OrderProcessedView(LoginRequiredMixin, TemplateView):
    template_name = "order_processed.html"
    use_case = None

    def __init__(self, use_case=None, **kwargs):
        super().__init__(**kwargs)
        self.use_case = use_case

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

        input = ShowProcessedOrderInput(
            token=str(token),
            user_id=request.user.id,
        )
        result = self.use_case.execute(input)

        if not result.success:
            return redirect("orders:my-orders")

        self.session_data = result
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "session": {
                "token": self.session_data.token,
                "order_id": self.session_data.order_id,
                "amount_total": self.session_data.amount_total,
            },
            "order": self.session_data.order_id,
            "items": [
                {
                    "product_id": i.product_id,
                    "product_name": i.product_name,
                    "unit_price": i.unit_price,
                    "quantity": i.quantity,
                    "line_total": i.line_total,
                }
                for i in self.session_data.items
            ],
        })
        return context
