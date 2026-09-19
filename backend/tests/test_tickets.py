import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.events.models import Event, EventStatus, Category
from apps.tickets.models import TicketType
from apps.accounts.models import Role

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestTickets:
    @pytest.fixture
    def organizer(self, django_user_model):
        return django_user_model.objects.create_user(
            email='organizer@test.com',
            password='testpassword',
            role=Role.ORGANIZER
        )
        
    @pytest.fixture
    def event(self, organizer):
        category = Category.objects.create(name='Test Category')
        from django.utils import timezone
        now = timezone.now()
        return Event.objects.create(
            organizer=organizer,
            category=category,
            title='Test Event',
            start_datetime=now,
            end_datetime=now,
            registration_start=now,
            registration_end=now,
            status=EventStatus.PUBLISHED
        )
        
    def test_create_ticket_type(self, api_client, organizer, event):
        api_client.force_authenticate(user=organizer)
        url = reverse('ticket-type-list')
        
        data = {
            'event': event.id,
            'name': 'VIP Pass',
            'price': '100.00',
            'quantity': 50,
            'max_per_order': 4
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'VIP Pass'
        
        ticket_type = TicketType.objects.get(id=response.data['id'])
        assert ticket_type.available_quantity == 50
        assert ticket_type.is_sold_out is False
