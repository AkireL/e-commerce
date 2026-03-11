from django.urls import path
from .views import (
    CreateOrderProductView,
    MyOrdersView,
    OrderProcessedView,
    remove_order_item,
    update_order_item,
)
from .api import OrderDetailView, OrderMarkPaidView

app_name = "orders"
urlpatterns = [
    path('my-orders', MyOrdersView.as_view(), name='my-orders'),
    path('add-product', CreateOrderProductView.as_view(), name='add_product_order'),
    path('processed/<uuid:token>/', OrderProcessedView.as_view(), name='order-processed'),
    path('cart/update-item/<int:pk>/', update_order_item, name='cart-update-item'),
    path('cart/remove-item/<int:pk>/', remove_order_item, name='cart-remove-item'),
    path('<int:pk>/', OrderDetailView.as_view(), name='api-order-detail'),
    path('<int:pk>/mark-paid/', OrderMarkPaidView.as_view(), name='api-order-mark-paid'),
]
