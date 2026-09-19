from rest_framework import serializers
from .models import Attendee

class AttendeeSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    
    class Meta:
        model = Attendee
        fields = [
            'id', 'event_title', 'ticket_type_name', 'ticket_identifier',
            'qr_code', 'is_checked_in', 'check_in_time', 'created_at'
        ]
        read_only_fields = fields
