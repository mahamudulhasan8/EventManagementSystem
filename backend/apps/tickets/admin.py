from django.contrib import admin
from .models import TicketType

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'quantity', 'sold_quantity', 'available_quantity', 'is_active')
    list_filter = ('is_active', 'event__organizer')
    search_fields = ('name', 'event__title')
    readonly_fields = ('sold_quantity',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event')
