from django.urls import path
from .views import CreateOrderProductView, MyOrdersView, OrderProcessedView

urlpatterns = [
    path('my-orders', MyOrdersView.as_view(), name='my-orders'),
    path('add-product', CreateOrderProductView.as_view(), name='add_product_order'),
    path('processed/<uuid:token>/', OrderProcessedView.as_view(), name='order-processed'),
]
