from django.contrib import admin

from .models import PaymentSession, PaymentItem


@admin.register(PaymentSession)
class PaymentSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "user", "status", "amount_total", "created_at")
    search_fields = ("order__id", "user__username", "token")
    list_filter = ("status", "created_at")


@admin.register(PaymentItem)
class PaymentItemAdmin(admin.ModelAdmin):
    list_display = ("session", "product_name", "quantity", "unit_price")
    search_fields = ("session__token", "product_name")
