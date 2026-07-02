import os
from typing import Optional

import requests
from django.urls import reverse

from core.internal_http import internal_get, internal_post


class PaymentsClient:
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

    def invalidate_payment_sessions(self, order_id: int) -> dict:
        self._ensure_token()
        url = reverse('payments:api-invalidate-sessions')
        response = internal_post(url, {'order_id': order_id}, self._token)
        return response

    def get_payment_completed_session(self, token: str) -> dict | None:
        self._ensure_token()
        response = internal_get(f'/payments/sessions/{token}/', self._token)
        return response.get('session')
