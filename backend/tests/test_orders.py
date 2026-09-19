import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.events.models import Event, EventStatus, Category
from apps.tickets.models import TicketType
from apps.accounts.models import Role
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestOrders:
    @pytest.fixture
    def organizer(self, django_user_model):
        return django_user_model.objects.create_user(email='org@test.com', password='pw', role=Role.ORGANIZER)
        
    @pytest.fixture
    def customer(self, django_user_model):
        return django_user_model.objects.create_user(email='cust@test.com', password='pw', role=Role.CUSTOMER)
        
    @pytest.fixture
    def event(self, organizer):
        category = Category.objects.create(name='Test Category')
        now = timezone.now()
        return Event.objects.create(
            organizer=organizer, category=category, title='Test Event',
            start_datetime=now, end_datetime=now, registration_start=now - timedelta(days=1),
            registration_end=now + timedelta(days=1), status=EventStatus.PUBLISHED
        )
        
    @pytest.fixture
    def ticket_type(self, event):
        return TicketType.objects.create(
            event=event, name='General', price=50.00, quantity=100, max_per_order=2
        )
        
    def test_create_order(self, api_client, customer, event, ticket_type):
        api_client.force_authenticate(user=customer)
        url = reverse('order-list')
        
        data = {
            'event_id': event.id,
            'items': [
                {'ticket_type_id': ticket_type.id, 'quantity': 1}
            ]
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.subtotal == 50.00
        
    def test_create_order_insufficient_inventory(self, api_client, customer, event, ticket_type):
        api_client.force_authenticate(user=customer)
        url = reverse('order-list')
        
        # Override inventory
        ticket_type.quantity = 1
        ticket_type.sold_quantity = 1
        ticket_type.save()
        
        data = {
            'event_id': event.id,
            'items': [{'ticket_type_id': ticket_type.id, 'quantity': 1}]
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Not enough tickets available' in response.data['detail']
