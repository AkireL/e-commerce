from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import View


class DeleteProductView(LoginRequiredMixin, View):
    delete_product_service = None

    def __init__(self, delete_product_service=None, **kwargs):
        super().__init__(**kwargs)
        self.delete_product_service = delete_product_service

    def post(self, request, pk):
        if not request.user.is_admin_or_editor():
            return redirect("products:product_list")

        self.delete_product_service.delete(pk)
        return redirect("products:product_list")