import uuid
from decimal import Decimal

from django.db import models
from django.urls import reverse


class PaymentSessionStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    COMPLETED = "completed", "Completado"
    FAILED = "failed", "Fallido"


class PaymentSession(models.Model):
    order_id = models.PositiveIntegerField(db_index=True, default=1)
    order_number = models.CharField(max_length=64, blank=True)
    user_id = models.PositiveIntegerField(db_index=True, default=1)
    user_username = models.CharField(max_length=150, blank=True)
    user_email = models.EmailField(blank=True)
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
        order_display = self.order_number or f"Orden {self.order_id}" if self.order_id else "Orden"
        return f"PaymentSession {self.token} ({order_display}) - {self.get_status_display()}"

    @property
    def is_completed(self) -> bool:
        return self.status == PaymentSessionStatus.COMPLETED

    def get_checkout_url(self) -> str:
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
