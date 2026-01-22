from django.urls import path
from .views import ListProductsView
from .views import CreateProductView

urlpatterns = [
     path('', ListProductsView.as_view(), name="product_list"),
     path('add', CreateProductView.as_view(), name="add_product"),
]