from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Category, Venue, Event, Speaker, EventSession, EventStatus
from .serializers import (
    CategorySerializer, VenueSerializer, EventListSerializer, 
    EventDetailSerializer, EventCreateUpdateSerializer, 
    SpeakerSerializer, EventSessionSerializer
)
from .filters import EventFilter
from apps.accounts.permissions import IsOrganizer, IsAdminOrOrganizer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city', 'country']

class EventViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'short_description', 'description']
    ordering_fields = ['start_datetime', 'created_at']
    ordering = ['start_datetime']
    lookup_field = 'slug'
    
    def get_queryset(self):
        user = self.request.user
        
        # If user is admin, they can see everything
        if user.is_authenticated and user.role == 'ADMIN':
            return Event.objects.all().select_related('category', 'venue', 'organizer')
            
        # If user is organizer, they can see their own events (including drafts)
        # plus published events by others
        if user.is_authenticated and user.role == 'ORGANIZER':
            return Event.objects.filter(
                models.Q(organizer=user) | 
                models.Q(status__in=[EventStatus.PUBLISHED, EventStatus.ONGOING, EventStatus.COMPLETED])
            ).select_related('category', 'venue', 'organizer')
            
        # Everyone else only sees public active events
        return Event.objects.filter(
            status__in=[EventStatus.PUBLISHED, EventStatus.ONGOING, EventStatus.COMPLETED]
        ).select_related('category', 'venue', 'organizer')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizer()]
        return [permissions.AllowAny()]
        
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class SpeakerViewSet(viewsets.ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    permission_classes = [IsOrganizer]
    
    def get_queryset(self):
        # Organizers can only manage speakers for their own events
        if getattr(self, 'swagger_fake_view', False):
            return Speaker.objects.none()
            
        return Speaker.objects.filter(event__organizer=self.request.user)


class EventSessionViewSet(viewsets.ModelViewSet):
    queryset = EventSession.objects.all()
    serializer_class = EventSessionSerializer
    permission_classes = [IsOrganizer]
    
    def get_queryset(self):
        # Organizers can only manage sessions for their own events
        if getattr(self, 'swagger_fake_view', False):
            return EventSession.objects.none()
            
        return EventSession.objects.filter(event__organizer=self.request.user)
