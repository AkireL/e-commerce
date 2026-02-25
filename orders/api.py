import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.models import Order


def order_detail_view(request, order_id):
    try:
        order = Order.objects.prefetch_related('items').get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    items = []
    for item in order.items.all():
        items.append({
            'id': item.id,
            'product_id': item.product_id,
            'product_name': item.product_name,
            'product_price': str(item.product_price),
            'quantity': item.quantity,
        })
    
    result = {
        'id': order.id,
        'user_id': order.user_id,
        'user_username': order.user_username,
        'user_email': order.user_email,
        'is_active': order.is_active,
        'items': items,
    }
    
    return JsonResponse({'order': result})


@csrf_exempt
@require_POST
def order_mark_paid_view(request, order_id):
    try:
        order = Order.objects.get(pk=order_id, is_active=True)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found or already paid'}, status=404)
    
    order.is_active = False
    order.save(update_fields=['is_active'])
    
    return JsonResponse({'success': True})
