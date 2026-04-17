from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View


class UpdateOrderItemView(LoginRequiredMixin, View):
    update_item_service = None
    
    def __init__(self, update_item_service, **kwargs):
        super().__init__(**kwargs)
        self.update_item_service = update_item_service

    def post(self, request, pk):
        quantity_raw = request.POST.get("quantity")
        quantity = 0

        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return _error_response("La cantidad debe ser un número válido.")

        if quantity < 1:
            return _error_response("La cantidad debe ser al menos 1.")
        
        return JsonResponse(self.update_item_service.execute(request.user, pk, quantity))
    
def _error_response( message, status=400):
    return JsonResponse({"success": False, "message": message}, status=status)
