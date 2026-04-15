from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from products.models import Product

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
  