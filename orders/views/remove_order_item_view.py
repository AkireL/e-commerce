from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from rest_framework.response import Response


class RemoveOrderItemView(LoginRequiredMixin, View):
    remove_item_service = None

    def __init__(self, remove_item_service, **kwargs):
        super().__init__(**kwargs)
        self.remove_item_service = remove_item_service
        
    def post(self, request, pk):
        response = self.remove_item_service.execute(request.user, pk)

        return Response(response)