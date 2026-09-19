from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.common.models import BaseModel

class DiscountType(models.TextChoices):
    PERCENTAGE = 'PERCENTAGE', 'Percentage'
    FIXED = 'FIXED', 'Fixed Amount'

class Coupon(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
        
    def is_valid(self, order_amount=0):
        if not self.is_active:
            return False, "Coupon is not active."
            
        now = timezone.now()
        if self.start_date > now:
            return False, "Coupon is not yet valid."
            
        if self.end_date and self.end_date < now:
            return False, "Coupon has expired."
            
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached."
            
        if order_amount < self.minimum_order_amount:
            return False, f"Minimum order amount of {self.minimum_order_amount} required."
            
        return True, "Valid"
        
    def calculate_discount(self, order_amount):
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = (order_amount * self.discount_value) / 100
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
            return discount
        return min(self.discount_value, order_amount)
