from django.urls import path
from .views import ListProductsView
from .views import CreateProductView
from django.conf.urls.static import static
from django.conf import settings
from .views import UpdateProductView

urlpatterns = [
     path('', ListProductsView.as_view(), name="product_list"),
     path('add', CreateProductView.as_view(), name="add_product"),
     path('edit/<int:pk>', UpdateProductView.as_view(), name="edit_product"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)