import os
from typing import Optional
from django.urls import reverse

import requests

from core.internal_http import internal_get, internal_post


def _get_service_token() -> Optional[str]:
    username = os.getenv('SERVICE_PAYMENTS_USERNAME', 'service_payments')
    password = os.getenv('SERVICE_PAYMENTS_PASSWORD', '')

    if not password:
        return None

    try:
        from django.conf import settings
        base_url = getattr(settings, 'INTERNAL_API_BASE_URL')
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


def mark_order_as_paid(order_id: int, user_id: int) -> dict:
    token = _service_token_cache.get('token') or _get_service_token()
    if token:
        _service_token_cache['token'] = token

    url = reverse('api-order-mark-paid', args=[order_id])
    response = internal_post(url, {'user_id': user_id}, token)
    return response


def get_order_detail(order_id: int) -> dict:
    token = _service_token_cache.get('token') or _get_service_token()
    if token:
        _service_token_cache['token'] = token
    
    url = reverse('api-order-detail', args=[order_id])
    response = internal_get(url, token)
    return response.get('order')
