from django.contrib import admin
from .models import Attendee

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('ticket_identifier', 'user', 'event', 'ticket_type', 'is_checked_in', 'check_in_time')
    list_filter = ('is_checked_in', 'event', 'ticket_type')
    search_fields = ('ticket_identifier', 'user__email', 'event__title')
    readonly_fields = ('ticket_identifier', 'qr_code')
