from core.internal_http import internal_get, internal_post


def mark_order_as_paid(order_id: int) -> dict:
    response = internal_post(f'/orders/api/order/{order_id}/mark-paid/', [])
    return response


def get_order_detail(order_id: int) -> dict:
    response = internal_get(f'/orders/api/order/{order_id}/')
    return response.get('order')
