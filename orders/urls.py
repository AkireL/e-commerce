from django.urls import path

from orders.views.update_order_item_view import UpdateOrderItemView
from orders.views.remove_order_item_view import RemoveOrderItemView
from orders.views.order_processed_view import OrderProcessedView
from orders.views.create_order_product_view import CreateOrderProductView
from orders.api import OrderDetailView, OrderMarkPaidView
from orders.views.show_orders_view import ShowMyOrdersView
from orders.services.remove_item_service import RemoveItemService
from orders.repositories.order_item_repository import OrderItemRepository
from orders.repositories import OrderRepository, OrderItemRepository
from orders.services.add_product_service import AddProductService
from orders.services.show_order_service import ShowOrderService
from orders.services.update_item_service import UpdateItemService
from orders.services.paid_order_service import PaidOrderService

app_name = "orders"

urlpatterns = [
    path(
        "my-orders",
        ShowMyOrdersView.as_view(
            show_order_service=ShowOrderService(
                order_repository=OrderRepository(),
                order_item_repository=OrderItemRepository(),
            )
        ),
        name="my-orders",
    ),
    path(
        "add-product",
        CreateOrderProductView.as_view(
            add_product_service=AddProductService(
                order_repository=OrderRepository(),
                order_item_repository=OrderItemRepository(),
            )
        ),
        name="add_product_order",
    ),
    path(
        "processed/<uuid:token>/", OrderProcessedView.as_view(), name="order-processed"
    ),
    path(
        "cart/update-item/<int:pk>/",
        UpdateOrderItemView.as_view(
            update_item_service=UpdateItemService(
                order_item_repository=OrderItemRepository()
            )
        ),
        name="cart-update-item",
    ),
    path(
        "cart/remove-item/<int:pk>/",
        RemoveOrderItemView.as_view(
            remove_item_service=RemoveItemService(
                order_item_repository=OrderItemRepository()
            )
        ),
        name="cart-remove-item",
    ),
    path("<int:pk>/", OrderDetailView.as_view(), name="api-order-detail"),
    path(
        "<int:pk>/mark-paid/",
        OrderMarkPaidView.as_view(
            paid_order_service=PaidOrderService(order_repository=OrderRepository())
        ),
        name="api-order-mark-paid",
    ),
]
