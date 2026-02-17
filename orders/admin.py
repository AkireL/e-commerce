from django.contrib import admin

from .models import Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ("product_name", "product_price", "quantity")
    fields = ("product_id", "product_name", "product_price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user_username", "user_email", "is_active", "order_at")
    list_filter = ("is_active", "order_at")
    search_fields = ("user_username", "user_email", "id")
    readonly_fields = ("order_at",)
    inlines = [OrderProductInline]
