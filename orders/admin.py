from django.contrib import admin
from .models import Order, OrderProduct

class OrderProductInLine(admin.TabularInline):
    model = OrderProduct
    extra = 0
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_active', 'order_at')
    list_filter = ('is_active', 'order_at')
    search_fields = ('user__username', 'id')
    model = Order
    inlines = [OrderProductInLine]
admin.site.register(Order, OrderAdmin)
