from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Attendee
from .serializers import AttendeeSerializer

class AttendeeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendeeSerializer
    
    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False):
            return Attendee.objects.none()
            
        if user.role == 'ADMIN':
            return Attendee.objects.all()
        elif user.role == 'ORGANIZER':
            return Attendee.objects.filter(event__organizer=user)
        else:
            return Attendee.objects.filter(user=user)
