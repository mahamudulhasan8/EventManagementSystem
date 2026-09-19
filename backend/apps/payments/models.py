from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel
from apps.orders.models import Order, PaymentStatus

class PaymentProvider(models.TextChoices):
    STRIPE = 'STRIPE', 'Stripe'
    SSLCOMMERZ = 'SSLCOMMERZ', 'SSLCommerz'
    BKASH = 'BKASH', 'bKash'
    NAGAD = 'NAGAD', 'Nagad'

class Payment(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    payment_method = models.CharField(max_length=50, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.order_number}"
