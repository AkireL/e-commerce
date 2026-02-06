from django.shortcuts import render
from .models import Product
from .forms import ProductForm
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class ListProductsView(LoginRequiredMixin, TemplateView):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'list.html', {
            'products': products
            })

class CreateProductView(LoginRequiredMixin, FormView):
    template_name = 'create.html'
    form_class = ProductForm
    success_url = reverse_lazy('product_list')


    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
class UpdateProductView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ["name", "description", "price", "stock", "available", "photo", ]
    success_url = reverse_lazy('product_list')
    template_name = 'create.html'
