import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from payments.models import PaymentSession, PaymentSessionStatus


def get_completed_session_view(request, token):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id required'}, status=400)
    
    try:
        session = PaymentSession.objects.prefetch_related('items').get(
            token=token,
            user_id=int(user_id),
            status=PaymentSessionStatus.COMPLETED,
        )
    except PaymentSession.DoesNotExist:
        return JsonResponse({'session': None})
    
    items = []
    for item in session.items.all():
        items.append({
            'id': item.id,
            'product_id': item.product_id,
            'product_name': item.product_name,
            'unit_price': str(item.unit_price),
            'quantity': item.quantity,
            'line_total': str(item.unit_price * item.quantity),
        })
    
    result = {
        'id': session.id,
        'token': str(session.token),
        'order_id': session.order_id,
        'order_number': session.order_number,
        'user_id': session.user_id,
        'user_username': session.user_username,
        'user_email': session.user_email,
        'status': session.status,
        'amount_total': str(session.amount_total),
        'items': items,
    }
    
    return JsonResponse({'session': result})


@csrf_exempt
@require_POST
def invalidate_sessions_view(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not order_id:
        return JsonResponse({'error': 'order_id required'}, status=400)
    
    deleted = PaymentSession.objects.filter(
        order_id=order_id,
        status=PaymentSessionStatus.PENDING
    ).delete()[0]
    
    return JsonResponse({'deleted': deleted})
