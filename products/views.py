from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, FormView, DetailView, View
from django.views.generic.edit import UpdateView
from .models import Product
from .forms import ProductForm

class ListProductsView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        can = self.request.user.is_admin_or_editor()
        context['can'] = {
            'products': {
                'edit':   can,
                'create': can,
                'delete': can,
            }
        }
        return context

class DetailProductView(LoginRequiredMixin, DetailView):
    template_name = "detail.html"
    model=Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        can = user.is_admin_or_editor()
        context['can'] = {
            'products': {
                'edit': can,
                'create': can,
                'delete': can,
            }
        }
        return context
    
class CreateProductView(LoginRequiredMixin, FormView):
    template_name = 'create.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
class UpdateProductView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('products:product_list')
    template_name = 'create.html'

class DeleteProductView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.is_admin_or_editor():
            return redirect("products:list_products")
        
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return redirect("products:products_list")