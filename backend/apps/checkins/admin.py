from django.contrib import admin
from .models import CheckInLog

@admin.register(CheckInLog)
class CheckInLogAdmin(admin.ModelAdmin):
    list_display = ('attendee', 'scanned_by', 'is_successful', 'timestamp')
    list_filter = ('is_successful', 'timestamp')
    search_fields = ('attendee__ticket_identifier', 'scanned_by__email')
    readonly_fields = ('attendee', 'scanned_by', 'timestamp', 'is_successful', 'notes')
