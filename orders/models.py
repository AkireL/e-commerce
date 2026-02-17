from django.db import models


class Order(models.Model):
    user_id = models.PositiveIntegerField(db_index=True)
    user_username = models.CharField(max_length=150, blank=True)
    user_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    order_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-order_at"]

    def __str__(self):
        username = self.user_username or f"Usuario {self.user_id}"
        return f"Order {self.id} - {username}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["product_name"]

    def __str__(self):
        return f"{self.quantity} x {self.product_name} (orden {self.order_id})"

    @property
    def line_total(self):
        return self.product_price * self.quantity
