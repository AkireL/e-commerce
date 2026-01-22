from django.shortcuts import render
from .models import Product
from .forms import ProductForm
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy

class ListProductsView(TemplateView):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'list.html', {
            'products': products
            })

class CreateProductView(FormView):
    template_name = 'create.html'
    form_class = ProductForm
    success_url = reverse_lazy('product_list')


    def form_valid(self, form):
        form.save()
        return super().form_valid(form)