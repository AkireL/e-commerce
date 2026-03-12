from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, DetailView
from django.views.generic.edit import UpdateView
from .models import Product
from .forms import ProductForm

class ListProductsView(LoginRequiredMixin, TemplateView):
    def get(self, request):
        can = request.user.is_admin_or_editor()

        products = Product.objects.all()
        return render(request, 'list.html', {
            'products': products,
            'can': {
                'products': {
                        'edit': can,
                        'create': can,
                        'delete': can,
                    }
                }
            })
    
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
