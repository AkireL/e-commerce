from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View

from orders.use_cases.update_item import UpdateItemInput


class UpdateOrderItemView(LoginRequiredMixin, View):
    def __init__(self, use_case=None, **kwargs):
        super().__init__(**kwargs)
        self.use_case = use_case

    def post(self, request, pk):
        quantity_raw = request.POST.get("quantity")

        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return _error_response("La cantidad debe ser un número válido.")

        if quantity < 1:
            return _error_response("La cantidad debe ser al menos 1.")

        input = UpdateItemInput(
            user_id=request.user.id,
            item_id=pk,
            quantity=quantity,
        )

        return JsonResponse(self.use_case.execute(input).__dict__)


def _error_response(message, status=400):
    return JsonResponse({"success": False, "message": message}, status=status)
