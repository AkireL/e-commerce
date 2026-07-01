import os
from typing import Optional

import requests
from django.urls import reverse

from core.internal_http import internal_get, internal_post


class ProductsClient:
    def __init__(self):
        self._token: Optional[str] = None

    def _ensure_token(self) -> None:
        if self._token:
            return
        username = os.getenv('SERVICE_ORDERS_USERNAME', 'service_orders')
        password = os.getenv('SERVICE_ORDERS_PASSWORD', '')
        if not password:
            return
        try:
            from django.conf import settings
            base_url = getattr(settings, 'INTERNAL_API_BASE_URL')
        except Exception:
            base_url = 'http://127.0.0.1:8000'
        try:
            response = requests.post(
                f'{base_url}/api/token/',
                data={'username': username, 'password': password},
                timeout=5,
            )
            if response.status_code == 200:
                self._token = response.json().get('access')
        except Exception:
            pass

    def get_products_available(self) -> list:
        self._ensure_token()
        url = reverse('products:api-products-available')
        response = internal_get(url, self._token)
        return response.get('products', [])

    def get_products_info(self, product_ids: list[int]) -> dict:
        self._ensure_token()
        url = reverse('products:api-products-info')
        response = internal_post(url, {'product_ids': product_ids}, self._token)
        return response.get('products', {})

    def get_product_info(self, product_id: int) -> dict | None:
        products = self.get_products_info([product_id])
        return products.get(str(product_id))

    def get_products_stock(self, product_ids: list[int]) -> dict:
        self._ensure_token()
        url = reverse('products:api-product-stock')
        response = internal_post(url, {'product_ids': product_ids}, self._token)
        return response.get('stocks', {})
