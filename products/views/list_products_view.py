from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from logger.logger import logger


class ListProductsView(LoginRequiredMixin, ListView):
    template_name = 'list.html'
    context_object_name = 'products'
    list_product_service = None

    def __init__(self, list_product_service=None, **kwargs):
        super().__init__(**kwargs)
        self.list_product_service = list_product_service

    def get_queryset(self):
        return self.list_product_service.get_products()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can'] = self.list_product_service.get_permissions(self.request.user)
        logger.warning(f"ListProductsView - User {self.request.user.username} accessed the product list view.")
        return context