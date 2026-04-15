from django.urls import path
from orders.views.update_order_item_view import UpdateOrderItemView
from orders.views.remove_order_item_view import RemoveOrderItemView
from orders.views.order_processed_view import OrderProcessedView
from orders.views.create_order_product_view import CreateOrderProductView
from orders.api import OrderDetailView, OrderMarkPaidView
from orders.views.show_orders_view import MyOrdersView

app_name = "orders"

urlpatterns = [
    path('my-orders', MyOrdersView.as_view(), name='my-orders'),
    path('add-product', CreateOrderProductView.as_view(), name='add_product_order'),
    path('processed/<uuid:token>/', OrderProcessedView.as_view(), name='order-processed'),
    path('cart/update-item/<int:pk>/', UpdateOrderItemView.as_view(), name='cart-update-item'),
    path('cart/remove-item/<int:pk>/', RemoveOrderItemView.as_view(), name='cart-remove-item'),
    path('<int:pk>/', OrderDetailView.as_view(), name='api-order-detail'),
    path('<int:pk>/mark-paid/', OrderMarkPaidView.as_view(), name='api-order-mark-paid'),
]
