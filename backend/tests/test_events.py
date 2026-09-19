import pytest
from django.urls import reverse
from rest_framework import status
from apps.events.models import Category, Venue, Event, EventStatus
from apps.accounts.models import Role
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestEvents:
    @pytest.fixture
    def organizer(self, django_user_model):
        return django_user_model.objects.create_user(
            email='organizer@test.com',
            password='testpassword',
            role=Role.ORGANIZER
        )
        
    @pytest.fixture
    def customer(self, django_user_model):
        return django_user_model.objects.create_user(
            email='customer@test.com',
            password='testpassword',
            role=Role.CUSTOMER
        )
        
    @pytest.fixture
    def category(self):
        return Category.objects.create(name='Tech Conference')
        
    @pytest.fixture
    def event(self, organizer, category):
        now = timezone.now()
        return Event.objects.create(
            organizer=organizer,
            category=category,
            title='Future Tech 2026',
            short_description='A cool tech conf',
            description='Very long description',
            start_datetime=now + timedelta(days=10),
            end_datetime=now + timedelta(days=12),
            registration_start=now,
            registration_end=now + timedelta(days=9),
            status=EventStatus.PUBLISHED
        )
        
    def test_list_published_events(self, api_client, event):
        url = reverse('event-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Future Tech 2026'
        
    def test_customer_cannot_create_event(self, api_client, customer, category):
        api_client.force_authenticate(user=customer)
        url = reverse('event-list')
        
        now = timezone.now()
        data = {
            'title': 'Hackathon',
            'category': category.id,
            'short_description': 'short',
            'description': 'long',
            'start_datetime': now + timedelta(days=10),
            'end_datetime': now + timedelta(days=12),
            'registration_start': now,
            'registration_end': now + timedelta(days=9),
            'status': EventStatus.DRAFT
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_organizer_can_create_event(self, api_client, organizer, category):
        api_client.force_authenticate(user=organizer)
        url = reverse('event-list')
        
        now = timezone.now()
        data = {
            'title': 'Hackathon',
            'category': category.id,
            'short_description': 'short',
            'description': 'long',
            'start_datetime': now + timedelta(days=10),
            'end_datetime': now + timedelta(days=12),
            'registration_start': now,
            'registration_end': now + timedelta(days=9),
            'status': EventStatus.DRAFT
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Hackathon'
        assert Event.objects.filter(title='Hackathon').exists()
