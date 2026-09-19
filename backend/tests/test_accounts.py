import pytest
from django.urls import reverse
from rest_framework import status
from apps.accounts.models import User, OrganizerProfile, Role

@pytest.mark.django_db
class TestAuthentication:
    def test_customer_registration(self, client):
        url = reverse('register_customer')
        data = {
            'email': 'customer@test.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'Customer'
        }
        
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert User.objects.filter(email='customer@test.com', role=Role.CUSTOMER).exists()
        
    def test_organizer_registration(self, client):
        url = reverse('register_organizer')
        data = {
            'email': 'organizer@test.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'Organizer',
            'organization_name': 'Awesome Events LLC'
        }
        
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        
        user = User.objects.get(email='organizer@test.com')
        assert user.role == Role.ORGANIZER
        assert OrganizerProfile.objects.filter(user=user, organization_name='Awesome Events LLC').exists()
        
    def test_login_success(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            email='user@test.com',
            password='testpassword'
        )
        
        url = reverse('token_obtain_pair')
        response = client.post(url, {'email': 'user@test.com', 'password': 'testpassword'})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        
    def test_login_failure(self, client):
        url = reverse('token_obtain_pair')
        response = client.post(url, {'email': 'nonexistent@test.com', 'password': 'wrong'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
