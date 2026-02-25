from core.internal_http import internal_get, internal_post


def get_products_available() -> list:
    response = internal_get('/product/api/products-available/')
    return response.get('products', [])


def get_products_info(product_ids: list[int]) -> dict:
    response = internal_post('/product/api/products-info/', {'product_ids': product_ids})
    return response.get('products', {})


def get_products_stock(product_ids: list[int]) -> dict:
    response = internal_post('/product/api/product-stock/', {'product_ids': product_ids})
    return response.get('stocks', {})


def invalidate_payment_sessions(order_id: int) -> dict:
    response = internal_post('/payments/api/invalidate-sessions/', {'order_id': order_id})
    return response


def get_payment_completed_session(token: str, user_id: int) -> dict | None:
    response = internal_get(f'/payments/api/get-completed-session/{token}/?user_id={user_id}')
    return response.get('session')
