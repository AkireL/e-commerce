from django.urls import path
from .views import (
    CreateOrderProductView,
    MyOrdersView,
    OrderProcessedView,
    remove_order_item,
    update_order_item,
)
from .api import order_detail_view, order_mark_paid_view

urlpatterns = [
    path('my-orders', MyOrdersView.as_view(), name='my-orders'),
    path('add-product', CreateOrderProductView.as_view(), name='add_product_order'),
    path('processed/<uuid:token>/', OrderProcessedView.as_view(), name='order-processed'),
    path('cart/update-item/<int:pk>/', update_order_item, name='cart-update-item'),
    path('cart/remove-item/<int:pk>/', remove_order_item, name='cart-remove-item'),
    path('api/order/<int:order_id>/', order_detail_view, name='api-order-detail'),
    path('api/order/<int:order_id>/mark-paid/', order_mark_paid_view, name='api-order-mark-paid'),
]
