from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView
from ..forms import ProductForm

class CreateProductView(LoginRequiredMixin, FormView):
    template_name = 'create.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    