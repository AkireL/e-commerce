import json
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings


def _get_base_url() -> str:
    if hasattr(settings, 'INTERNAL_API_BASE_URL'):
        return settings.INTERNAL_API_BASE_URL
    return 'http://127.0.0.1:8000'


def internal_post(url_path: str, data: dict[str, Any]) -> dict[str, Any]:
    url = f"{_get_base_url()}{url_path}"
    request = Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    
    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except URLError as e:
        return {'error': str(e), 'success': False}
    except Exception as e:
        return {'error': str(e), 'success': False}


def internal_get(url_path: str) -> dict[str, Any]:
    url = f"{_get_base_url()}{url_path}"
    request = Request(
        url,
        headers={
            'Content-Type': 'application/json',
        },
        method='GET',
    )
    
    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except URLError as e:
        return {'error': str(e), 'success': False}
    except Exception as e:
        return {'error': str(e), 'success': False}
