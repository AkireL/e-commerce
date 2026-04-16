import json
from typing import Any, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings


def _get_base_url() -> str:
    if hasattr(settings, 'INTERNAL_API_BASE_URL'):
        return settings.INTERNAL_API_BASE_URL
    return 'http://127.0.0.1:8000'


def _get_headers(token: Optional[str] = None) -> dict:
    headers = {
        'Content-Type': 'application/json',
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def internal_post(url_path: str, data: dict[str, Any], token: Optional[str] = None) -> dict[str, Any]:
    url = f"{_get_base_url()}{url_path}"
    
    request = Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=_get_headers(token),
        method='POST',
    )
    
    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except URLError as e:
        return {'code': 500, 'status_code': 500, 'error': str(e), 'success': False}
    except Exception as e:
        return {'code': None, 'status_code': None, 'error': str(e), 'success': False}


def internal_get(url_path: str, token: Optional[str] = None) -> dict[str, Any]:
    url = f"{_get_base_url()}{url_path}"
    request = Request(
        url,
        headers=_get_headers(token),
        method='GET',
    )
    
    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except URLError as e:
        return {'error': str(e), 'success': False}
    except Exception as e:
        return {'error': str(e), 'success': False}
