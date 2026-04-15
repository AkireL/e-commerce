from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from products.views.api.available_product_view import ProductsAvailableView 
from products.views.api.detail_product_view import ProductsInfoView
from products.views.api.stock_product_view import ProductsStockView
from products.views.create_product_view import CreateProductView
from products.views.delete_product_view import DeleteProductView
from products.views.list_products_view import ListProductsView
from products.views.show_product_view import DetailProductView
from products.views.update_product_view import UpdateProductView

app_name = "products"
urlpatterns = [
    path("", ListProductsView.as_view(), name="product_list"),
    path("add", CreateProductView.as_view(), name="add_product"),
    path("<int:pk>", DetailProductView.as_view(), name="detail_product"),
    path("edit/<int:pk>", UpdateProductView.as_view(), name="edit_product"),
    path("delete/<int:pk>", DeleteProductView.as_view(), name="delete_product"),
    path(
        "api/products-available/",
        ProductsAvailableView.as_view(),
        name="api-products-available",
    ),
    path("api/products-info/", ProductsInfoView.as_view(), name="api-products-info"),
    path("api/product-stock/", ProductsStockView.as_view(), name="api-product-stock"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
