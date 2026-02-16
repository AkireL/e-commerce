import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class PaymentSessionStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    COMPLETED = "completed", "Completado"
    FAILED = "failed", "Fallido"


class PaymentSession(models.Model):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payment_sessions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_sessions")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=PaymentSessionStatus.choices, default=PaymentSessionStatus.PENDING)
    amount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="MXN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"PaymentSession {self.token} - {self.get_status_display()}"

    @property
    def is_completed(self) -> bool:
        return self.status == PaymentSessionStatus.COMPLETED

    def get_checkout_url(self) -> str:
        from django.urls import reverse

        return reverse("payments:checkout", args=[self.token])


class PaymentItem(models.Model):
    session = models.ForeignKey(PaymentSession, on_delete=models.CASCADE, related_name="items")
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ("product_name",)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product_name}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity
