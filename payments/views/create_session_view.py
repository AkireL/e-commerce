import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect

from payments.exceptions import EmptyOrderError
from payments.services.payment_service import PaymentService

@login_required
def create_session_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    order_id = request.POST.get("order_id")
    items_raw = request.POST.getlist("items")
    
    if not order_id or not items_raw:
        messages.error(request, "No se encontró información de la orden.")
        return redirect("orders:my-orders")
    
    try:
        items = [json.loads(item) for item in items_raw]
    except json.JSONDecodeError:
        messages.error(request, "Error al procesar los productos.")
        return redirect("orders:my-orders")
    
    if not items:
        messages.error(request, "La orden no tiene productos para pagar.")
        return redirect("orders:my-orders")

    order_data = {
        "id": int(order_id),
        "items": items,
    }

    try:
        session_data = PaymentService().create_payment_session(request.user, order_data)
        messages.info(request, "Redirigiéndote a la pasarela de pago simulada.")
        
        return redirect("payments:checkout", token=session_data.token)
    except EmptyOrderError as exc:
        messages.error(request, str(exc))
        return redirect("orders:my-orders")


