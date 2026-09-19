from django.db import models
from django.core.files.base import ContentFile
from apps.common.models import BaseModel
from apps.accounts.models import User
from apps.events.models import Event
from apps.tickets.models import TicketType
from apps.orders.models import OrderItem
import qrcode
from io import BytesIO
import uuid
import json

class Attendee(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attended_events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.RESTRICT)
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='attendee')
    
    # Check-in identifier
    ticket_identifier = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_code = models.ImageField(upload_to='tickets/qr/', blank=True, null=True)
    
    is_checked_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'event', 'order_item']

    def __str__(self):
        return f"{self.user.email} - {self.event.title}"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        # Data encoded in QR
        qr_data = json.dumps({
            "ticket_id": str(self.ticket_identifier),
            "event_id": str(self.event.id),
            "user_email": self.user.email
        })
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        file_name = f"qr_{self.ticket_identifier}.png"
        
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
