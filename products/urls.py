from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .models import Product
from .views import ListProductsView, CreateProductView, UpdateProductView
from .api import products_info_view, products_stock_view, products_available_view


@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("product_list")


urlpatterns = [
    path('', ListProductsView.as_view(), name="product_list"),
    path('add', CreateProductView.as_view(), name="add_product"),
    path('edit/<int:pk>', UpdateProductView.as_view(), name="edit_product"),
    path('delete/<int:pk>', delete_product, name="delete_product"),
    path('api/products-available/', products_available_view, name='api-products-available'),
    path('api/products-info/', products_info_view, name='api-products-info'),
    path('api/product-stock/', products_stock_view, name='api-product-stock'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
