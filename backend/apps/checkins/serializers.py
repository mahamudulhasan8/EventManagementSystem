from rest_framework import serializers
from .models import CheckInLog

class CheckInSerializer(serializers.Serializer):
    ticket_identifier = serializers.UUIDField()

class CheckInLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInLog
        fields = '__all__'
        read_only_fields = ['id', 'attendee', 'scanned_by', 'timestamp', 'created_at', 'updated_at']
