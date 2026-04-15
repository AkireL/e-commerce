from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from products.models import Product

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
  
