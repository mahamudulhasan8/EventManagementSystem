from rest_framework import serializers
from .models import Category, Venue, Event, Speaker, EventSession, EventStatus

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class EventSessionSerializer(serializers.ModelSerializer):
    speaker_details = SpeakerSerializer(source='speaker', read_only=True)
    
    class Meta:
        model = EventSession
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class EventListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'short_description', 'cover_image',
            'start_datetime', 'end_datetime', 'status', 'is_featured',
            'category', 'venue'
        ]
        
class EventDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    sessions = EventSessionSerializer(many=True, read_only=True)
    speakers = SpeakerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'organizer', 'created_at', 'updated_at']

class EventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'category', 'venue', 'title', 'short_description', 'description',
            'cover_image', 'start_datetime', 'end_datetime', 'registration_start',
            'registration_end', 'capacity', 'status', 'is_featured', 'terms'
        ]
        
    def validate(self, attrs):
        if attrs.get('start_datetime') and attrs.get('end_datetime'):
            if attrs['start_datetime'] >= attrs['end_datetime']:
                raise serializers.ValidationError({"end_datetime": "End time must be after start time."})
                
        if attrs.get('registration_start') and attrs.get('registration_end'):
            if attrs['registration_start'] >= attrs['registration_end']:
                raise serializers.ValidationError({"registration_end": "Registration end must be after registration start."})
                
        return attrs
