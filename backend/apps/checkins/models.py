from django.db import models
from apps.common.models import BaseModel
from apps.attendees.models import Attendee
from apps.accounts.models import User

class CheckInLog(BaseModel):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, related_name='checkin_logs')
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='scans_performed')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Scan for {self.attendee.ticket_identifier} at {self.timestamp}"
