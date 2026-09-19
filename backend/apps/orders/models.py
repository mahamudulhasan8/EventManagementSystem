from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User
from apps.events.models import Event
from apps.tickets.models import TicketType
from apps.coupons.models import Coupon
from django.utils.translation import gettext_lazy as _

class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    CONFIRMED = 'CONFIRMED', _('Confirmed')
    CANCELLED = 'CANCELLED', _('Cancelled')
    REFUNDED = 'REFUNDED', _('Refunded')

class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    PAID = 'PAID', _('Paid')
    FAILED = 'FAILED', _('Failed')
    REFUNDED = 'REFUNDED', _('Refunded')

class Order(BaseModel):
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='orders')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"
        
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate OR-TIMESTAMP-RANDOM format
            import time
            import random
            import string
            timestamp = str(int(time.time()))
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.order_number = f"OR-{timestamp}-{random_str}"
        super().save(*args, **kwargs)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.ticket_type.name} (Order {self.order.order_number})"
