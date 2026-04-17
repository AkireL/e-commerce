from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from ..forms import ProductForm


class UpdateProductView(LoginRequiredMixin, UpdateView):
    form_class = ProductForm
    success_url = reverse_lazy('products:product_list')
    template_name = 'create.html'
    update_product_service = None

    def __init__(self, update_product_service=None, **kwargs):
        super().__init__(**kwargs)
        self.update_product_service = update_product_service

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.update_product_service.get_product(pk)

    def get_queryset(self):
        return [self.update_product_service.get_product(self.kwargs.get(self.pk_url_kwarg))]

    def form_valid(self, form):
        self.update_product_service.update(self.kwargs.get(self.pk_url_kwarg), form.cleaned_data)
        return super().form_valid(form)