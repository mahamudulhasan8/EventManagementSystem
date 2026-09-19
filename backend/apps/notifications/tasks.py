from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationType

@shared_task
def send_email_notification_task(user_id, subject, message, from_email=None):
    from apps.accounts.models import User
    try:
        user = User.objects.get(id=user_id)
        if not from_email:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            
        send_mail(
            subject,
            message,
            from_email,
            [user.email],
            fail_silently=False,
        )
        return f"Email sent to {user.email}"
    except User.DoesNotExist:
        return "User not found"

@shared_task
def create_notification_task(user_id, title, message, notification_type=NotificationType.IN_APP):
    Notification.objects.create(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type
    )
    
    if notification_type in [NotificationType.EMAIL, NotificationType.BOTH]:
        send_email_notification_task.delay(user_id, title, message)
        
    return f"Notification created for user {user_id}"
