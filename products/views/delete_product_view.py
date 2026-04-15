from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from ..models import Product


class DeleteProductView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.is_admin_or_editor():
            return redirect("products:product_list")
        
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return redirect("products:product_list")