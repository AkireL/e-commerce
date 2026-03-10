from rest_framework import serializers
from payments.models import PaymentSession, PaymentItem


class PaymentItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PaymentItem
        fields = ['id', 'product_id', 'product_name', 'unit_price', 'quantity', 'line_total']


class PaymentSessionSerializer(serializers.ModelSerializer):
    items = PaymentItemSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentSession
        fields = [
            'id', 'token', 'order_id', 'order_number', 'user_id',
            'user_username', 'user_email', 'status', 'amount_total', 'items'
        ]
