from django.urls import path
from .views import MyOrdersView, CreateOrderProductView

urlpatterns = [
    path('my-orders', MyOrdersView.as_view(), name='my-orders'),
    path('add-product', CreateOrderProductView.as_view(), name='add_product_order'),
]