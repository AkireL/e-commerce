from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from products.repositories import ProductRepository
from products.services.list_product_service import ListProductService
from products.services.create_product_service import CreateProductService
from products.services.get_product_service import GetProductService
from products.services.update_product_service import UpdateProductService
from products.services.delete_product_service import DeleteProductService
from products.services.get_products_info_service import GetProductsInfoService
from products.views.api.available_product_view import ProductsAvailableView 
from products.views.api.detail_product_view import ProductsInfoView
from products.views.api.stock_product_view import ProductsStockView
from products.views.create_product_view import CreateProductView
from products.views.delete_product_view import DeleteProductView
from products.views.list_products_view import ListProductsView
from products.views.show_product_view import DetailProductView
from products.views.update_product_view import UpdateProductView

app_name = "products"

product_repository = ProductRepository()

urlpatterns = [
    path("", ListProductsView.as_view(
        list_product_service=ListProductService(product_repository=product_repository)
    ), name="product_list"),
    path("add", CreateProductView.as_view(
        create_product_service=CreateProductService(product_repository=product_repository)
    ), name="add_product"),
    path("<int:pk>", DetailProductView.as_view(
        get_product_service=GetProductService(product_repository=product_repository)
    ), name="detail_product"),
    path("edit/<int:pk>", UpdateProductView.as_view(
        update_product_service=UpdateProductService(product_repository=product_repository)
    ), name="edit_product"),
    path("delete/<int:pk>", DeleteProductView.as_view(
        delete_product_service=DeleteProductService(product_repository=product_repository)
    ), name="delete_product"),
    path(
        "api/products-available/",
        ProductsAvailableView.as_view(),
        name="api-products-available",
    ),
    path("api/products-info/", ProductsInfoView.as_view(
        get_products_info_service=GetProductsInfoService(product_repository=product_repository)
    ), name="api-products-info"),
    path("api/product-stock/", ProductsStockView.as_view(), name="api-product-stock"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)