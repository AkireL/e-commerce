import os
from typing import Optional
from django.urls import reverse
import requests

from core.internal_http import internal_get, internal_post


class OrderClient:
    """
    Cliente interno para comunicación con el servicio de orders.
    Maneja autenticación y reintento automático si el token expira.
    """

    def __init__(self):
        self._token: Optional[str] = None

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _get_base_url(self) -> str:
        try:
            from django.conf import settings
            return getattr(settings, 'INTERNAL_API_BASE_URL', 'http://127.0.0.1:8000')
        except Exception:
            return 'http://127.0.0.1:8000'

    def _fetch_token(self) -> Optional[str]:
        username = os.getenv('SERVICE_PAYMENTS_USERNAME', 'service_payments')
        password = os.getenv('SERVICE_PAYMENTS_PASSWORD', '')

        if not password:
            return None

        try:
            response = requests.post(
                f'{self._get_base_url()}/api/token/',
                data={'username': username, 'password': password},
                timeout=5,
            )
            if response.status_code == 200:
                return response.json().get('access')
        except Exception:
            pass

        return None

    def _get_token(self) -> Optional[str]:
        if not self._token:
            self._token = self._fetch_token()
        return self._token

    def _invalidate_token(self):
        self._token = None

    # ------------------------------------------------------------------
    # Requests con reintento si el token expiró (401)
    # ------------------------------------------------------------------

    def _post(self, url: str, data: dict) -> dict:
        token = self._get_token()
        response = internal_post(url, data, token)

        if response.get('status_code') == 401:
            self._invalidate_token()
            token = self._get_token()
            response = internal_post(url, data, token)

        return response

    def _get(self, url: str) -> dict:
        token = self._get_token()
        response = internal_get(url, token)

        if response.get('status_code') == 401:
            self._invalidate_token()
            token = self._get_token()
            response = internal_get(url, token)

        return response

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def mark_order_as_paid(self, order_id: int, user_id: int) -> dict:
        url = reverse('orders:api-order-mark-paid', args=[order_id])
        return self._post(url, {'user_id': user_id})

    def get_order_detail(self, order_id: int) -> dict:
        url = reverse('orders:api-order-detail', args=[order_id])
        response = self._get(url)
        return response.get('order')


order_client = OrderClient()