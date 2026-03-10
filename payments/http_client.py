import os
from typing import Optional

import requests

from core.internal_http import internal_get, internal_post


def _get_service_token() -> Optional[str]:
    username = os.getenv('SERVICE_PAYMENTS_USERNAME', 'service_payments')
    password = os.getenv('SERVICE_PAYMENTS_PASSWORD', '')

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


def mark_order_as_paid(order_id: int) -> dict:
    token = _service_token_cache.get('token') or _get_service_token()
    if token:
        _service_token_cache['token'] = token
    response = internal_post(f'/orders/api/order/{order_id}/mark-paid/', {}, token)
    return response


def get_order_detail(order_id: int) -> dict:
    token = _service_token_cache.get('token') or _get_service_token()
    if token:
        _service_token_cache['token'] = token
    response = internal_get(f'/orders/api/order/{order_id}/', token)
    return response.get('order')
