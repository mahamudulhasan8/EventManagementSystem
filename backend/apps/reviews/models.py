from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import BaseModel
from apps.accounts.models import User
from apps.events.models import Event

class Review(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True) # Admin can moderate

    class Meta:
        unique_together = ['user', 'event'] # One review per user per event

    def __str__(self):
        return f"{self.rating} stars for {self.event.title} by {self.user.email}"
