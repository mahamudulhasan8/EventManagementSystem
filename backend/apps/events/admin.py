from django.contrib import admin
from .models import Category, Venue, Event, Speaker, EventSession

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'capacity')
    search_fields = ('name', 'city', 'country')
    list_filter = ('city', 'country')

class SpeakerInline(admin.TabularInline):
    model = Speaker
    extra = 1

class EventSessionInline(admin.TabularInline):
    model = EventSession
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'category', 'start_datetime', 'status', 'is_featured')
    list_filter = ('status', 'is_featured', 'category')
    search_fields = ('title', 'organizer__email', 'organizer__organizer_profile__organization_name')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    inlines = [SpeakerInline, EventSessionInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organizer', 'category', 'venue')
