from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View

from orders.use_cases.remove_item import RemoveItemInput


class RemoveOrderItemView(LoginRequiredMixin, View):
    def __init__(self, use_case=None, **kwargs):
        super().__init__(**kwargs)
        self.use_case = use_case

    def post(self, request, pk):
        input = RemoveItemInput(
            user_id=request.user.id,
            item_id=pk,
        )
        result = self.use_case.execute(input)
        return JsonResponse(result.__dict__)
