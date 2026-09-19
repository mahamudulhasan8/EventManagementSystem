from django.db import models
from django.core.validators import MinValueValidator
from apps.common.models import BaseModel
from apps.events.models import Event

class TicketType(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    quantity = models.PositiveIntegerField(help_text="Total number of tickets available for this type.")
    sold_quantity = models.PositiveIntegerField(default=0, help_text="Number of tickets already sold.")
    
    sale_start = models.DateTimeField(null=True, blank=True)
    sale_end = models.DateTimeField(null=True, blank=True)
    
    max_per_order = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['price']
        unique_together = ['event', 'name']

    def __str__(self):
        return f"{self.name} - {self.event.title}"
        
    @property
    def available_quantity(self):
        return max(0, self.quantity - self.sold_quantity)
        
    @property
    def is_sold_out(self):
        return self.available_quantity <= 0
