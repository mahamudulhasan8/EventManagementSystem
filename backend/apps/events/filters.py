import django_filters
from .models import Event, Category, Venue

class EventFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    date_from = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='lte')
    status = django_filters.CharFilter(field_name='status')
    category_slug = django_filters.CharFilter(field_name='category__slug')
    city = django_filters.CharFilter(field_name='venue__city', lookup_expr='iexact')
    organizer_id = django_filters.UUIDFilter(field_name='organizer__id')
    
    class Meta:
        model = Event
        fields = ['status', 'is_featured', 'category', 'venue']
