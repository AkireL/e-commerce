from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView


class DetailProductView(LoginRequiredMixin, DetailView):
    template_name = "detail.html"
    model = None
    get_product_service = None

    def __init__(self, get_product_service=None, **kwargs):
        super().__init__(**kwargs)
        self.get_product_service = get_product_service

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.get_product_service.get_product(pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can'] = self.get_product_service.get_permissions(self.request.user)
        return context