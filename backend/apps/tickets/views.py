from rest_framework import viewsets, permissions
from .models import TicketType
from .serializers import TicketTypeSerializer
from apps.accounts.permissions import IsOrganizer
from django_filters.rest_framework import DjangoFilterBackend

class TicketTypeViewSet(viewsets.ModelViewSet):
    serializer_class = TicketTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'is_active']
    
    def get_queryset(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Organizers can only modify their own events' tickets
            if getattr(self, 'swagger_fake_view', False):
                return TicketType.objects.none()
            return TicketType.objects.filter(event__organizer=self.request.user)
            
        # Anyone can view active ticket types
        return TicketType.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizer()]
        return [permissions.AllowAny()]
