from django.urls import path

from orders.clients.products_client import ProductsClient
from orders.clients.payments_client import PaymentsClient
from orders.repositories.order_repository import OrderRepository
from orders.use_cases.add_product import AddProductUseCase
from orders.use_cases.show_order import ShowOrderUseCase
from orders.use_cases.update_item import UpdateItemUseCase
from orders.use_cases.remove_item import RemoveItemUseCase
from orders.use_cases.order_detail import OrderDetailUseCase
from orders.use_cases.paid_order import PaidOrderUseCase
from orders.use_cases.show_processed_order import ShowProcessedOrderUseCase
from orders.views.create_order_product_view import CreateOrderProductView
from orders.views.show_orders_view import ShowMyOrdersView
from orders.views.update_order_item_view import UpdateOrderItemView
from orders.views.remove_order_item_view import RemoveOrderItemView
from orders.views.order_processed_view import OrderProcessedView
from orders.api import OrderDetailView, OrderMarkPaidView

app_name = "orders"

urlpatterns = [
    path(
        "my-orders",
        ShowMyOrdersView.as_view(
            use_case=ShowOrderUseCase(
                order_repo=OrderRepository(),
                product_client=ProductsClient(),
            )
        ),
        name="my-orders",
    ),
    path(
        "add-product",
        CreateOrderProductView.as_view(
            use_case=AddProductUseCase(
                order_repo=OrderRepository(),
                product_client=ProductsClient(),
            )
        ),
        name="add_product_order",
    ),
    path(
        "processed/<uuid:token>/",
        OrderProcessedView.as_view(
            use_case=ShowProcessedOrderUseCase(
                payments_client=PaymentsClient(),
            )
        ),
        name="order-processed",
    ),
    path(
        "cart/update-item/<int:pk>/",
        UpdateOrderItemView.as_view(
            use_case=UpdateItemUseCase(
                order_repo=OrderRepository(),
                product_client=ProductsClient(),
                payments_client=PaymentsClient(),
            )
        ),
        name="cart-update-item",
    ),
    path(
        "cart/remove-item/<int:pk>/",
        RemoveOrderItemView.as_view(
            use_case=RemoveItemUseCase(
                order_repo=OrderRepository(),
                payments_client=PaymentsClient(),
            )
        ),
        name="cart-remove-item",
    ),
    path(
        "<int:pk>/",
        OrderDetailView.as_view(
            use_case=OrderDetailUseCase(order_repo=OrderRepository())
        ),
        name="api-order-detail",
    ),
    path(
        "<int:pk>/mark-paid/",
        OrderMarkPaidView.as_view(
            use_case=PaidOrderUseCase(order_repo=OrderRepository())
        ),
        name="api-order-mark-paid",
    ),
]
