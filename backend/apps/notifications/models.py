from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User

class NotificationType(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    IN_APP = 'IN_APP', 'In-App'
    BOTH = 'BOTH', 'Both'

class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.IN_APP)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.title}"
