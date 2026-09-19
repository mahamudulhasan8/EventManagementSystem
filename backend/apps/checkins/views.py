from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from .serializers import CheckInSerializer
from apps.attendees.models import Attendee
from .models import CheckInLog

class CheckInView(views.APIView):
    # Depending on requirements, this might be restricted to IsStaff/IsOrganizer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(request=CheckInSerializer, responses={200: dict})
    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ticket_id = serializer.validated_data['ticket_identifier']
        user = request.user
        
        try:
            attendee = Attendee.objects.get(ticket_identifier=ticket_id)
        except Attendee.DoesNotExist:
            return Response({"detail": "Invalid ticket ID."}, status=status.HTTP_404_NOT_FOUND)
            
        # Permission check: Is the user authorized to scan for this event?
        # Organizers, Admins, or assigned Staff can scan.
        is_authorized = user.role == 'ADMIN' or \
                        (user.role == 'ORGANIZER' and attendee.event.organizer == user) or \
                        user.role == 'STAFF' # Assuming STAFF can scan any event, can be refined
                        
        if not is_authorized:
            return Response({"detail": "Not authorized to scan this ticket."}, status=status.HTTP_403_FORBIDDEN)
            
        if attendee.is_checked_in:
            CheckInLog.objects.create(
                attendee=attendee,
                scanned_by=user,
                is_successful=False,
                notes="Ticket already checked in."
            )
            return Response({"detail": "Ticket already checked in."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Process check-in
        attendee.is_checked_in = True
        attendee.check_in_time = timezone.now()
        attendee.save()
        
        CheckInLog.objects.create(
            attendee=attendee,
            scanned_by=user,
            is_successful=True
        )
        
        return Response({"detail": "Check-in successful.", "attendee": attendee.user.email})
