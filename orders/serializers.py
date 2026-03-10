from rest_framework import serializers
from orders.models import Order, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderProduct
        fields = ['id', 'product_id', 'product_name', 'product_price', 'quantity', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'user_username', 'user_email', 'is_active', 'order_at', 'items']
