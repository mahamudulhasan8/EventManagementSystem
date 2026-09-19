from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemCreateSerializer(serializers.Serializer):
    ticket_type_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()
    items = OrderItemCreateSerializer(many=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'ticket_type_name', 'quantity', 'unit_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, allow_null=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'event', 'event_title', 'subtotal', 
            'discount', 'tax', 'service_fee', 'total', 'coupon_code', 
            'status', 'payment_status', 'created_at', 'items'
        ]
        read_only_fields = fields
