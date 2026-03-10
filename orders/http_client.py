import os
import json
from typing import Optional

import requests

from core.internal_http import internal_get, internal_post


def _get_service_token() -> Optional[str]:
    username = os.getenv('SERVICE_ORDERS_USERNAME', 'service_orders')
    password = os.getenv('SERVICE_ORDERS_PASSWORD', '')

    if not password:
        return None

    try:
        from django.conf import settings
        base_url = getattr(settings, 'INTERNAL_API_BASE_URL', 'http://127.0.0.1:8000')
    except Exception:
        base_url = 'http://127.0.0.1:8000'

    try:
        response = requests.post(
            f'{base_url}/api/token/',
            data={'username': username, 'password': password},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get('access')
    except Exception:
        pass

    return None


_service_token_cache = {'token': None}


def get_products_available() -> list:
    token = _service_token_cache.get('token') or _get_service_token()
    if token:
        _service_token_cache['token'] = token
    response = internal_get('/product/api/products-available/', token)
    return response.get('products', [])


def get_products_info(product_ids: list[int]) -> dict:
    token = _service_token_cache.get('token') or _get_service_token()
    if token:
        _service_token_cache['token'] = token
    response = internal_post('/product/api/products-info/', {'product_ids': product_ids}, token)
    return response.get('products', {})


def get_products_stock(product_ids: list[int]) -> dict:
    token = _service_token_cache.get('token') or _get_service_token()
    if token:
        _service_token_cache['token'] = token
    response = internal_post('/product/api/product-stock/', {'product_ids': product_ids}, token)
    return response.get('stocks', {})


def invalidate_payment_sessions(order_id: int) -> dict:
    token = _service_token_cache.get('token') or _get_service_token()
    if token:
        _service_token_cache['token'] = token
    response = internal_post('/payments/api/sessions/invalidate/', {'order_id': order_id}, token)
    return response


def get_payment_completed_session(token: str, user_id: int) -> dict | None:
    service_token = _service_token_cache.get('token') or _get_service_token()
    if service_token:
        _service_token_cache['token'] = service_token
    response = internal_get(f'/payments/api/sessions/{token}/?user_id={user_id}', service_token)
    return response.get('session')
