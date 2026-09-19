from rest_framework import serializers
from .models import TicketType
from django.utils import timezone

class TicketTypeSerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TicketType
        fields = [
            'id', 'event', 'name', 'description', 'price', 
            'quantity', 'sold_quantity', 'available_quantity', 
            'is_sold_out', 'sale_start', 'sale_end', 
            'max_per_order', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'sold_quantity', 'created_at']

    def validate(self, attrs):
        if attrs.get('sale_start') and attrs.get('sale_end'):
            if attrs['sale_start'] >= attrs['sale_end']:
                raise serializers.ValidationError({"sale_end": "Sale end must be after sale start."})
        return attrs
