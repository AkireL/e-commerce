import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from products.models import Product


@require_GET
def products_available_view(request):
    products = Product.objects.filter(available=True)
    
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock,
            'available': product.available,
            'photo_url': product.photo.url if product.photo else None,
        })
    
    return JsonResponse({'products': result})


@csrf_exempt
@require_POST
def products_info_view(request):
    try:
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not isinstance(product_ids, list):
        return JsonResponse({'error': 'product_ids must be a list'}, status=400)
    
    products = Product.objects.filter(id__in=product_ids)
    
    result = {}
    for product in products:
        result[str(product.id)] = {
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock,
            'available': product.available,
            'photo_url': product.photo.url if product.photo else None,
        }
    
    return JsonResponse({'products': result})


@csrf_exempt
@require_POST
def products_stock_view(request):
    try:
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not isinstance(product_ids, list):
        return JsonResponse({'error': 'product_ids must be a list'}, status=400)
    
    products = Product.objects.filter(id__in=product_ids).values('id', 'stock')
    
    result = {}
    for product in products:
        result[str(product['id'])] = product['stock']
    
    return JsonResponse({'stocks': result})
