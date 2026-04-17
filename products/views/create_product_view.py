from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView
from ..forms import ProductForm


class CreateProductView(LoginRequiredMixin, FormView):
    template_name = 'create.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:product_list')
    create_product_service = None

    def __init__(self, create_product_service=None, **kwargs):
        super().__init__(**kwargs)
        self.create_product_service = create_product_service

    def form_valid(self, form):
        self.create_product_service.create(form.cleaned_data)
        return super().form_valid(form)