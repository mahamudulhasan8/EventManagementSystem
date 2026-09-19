import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.events.models import Event, EventStatus, Category
from apps.orders.models import Order
from apps.payments.models import Payment, PaymentProvider, PaymentStatus
from apps.accounts.models import Role
from django.utils import timezone

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestPayments:
    @pytest.fixture
    def customer(self, django_user_model):
        return django_user_model.objects.create_user(email='cust@test.com', password='pw', role=Role.CUSTOMER)
        
    @pytest.fixture
    def order(self, customer, django_user_model):
        organizer = django_user_model.objects.create_user(email='org@test.com', password='pw', role=Role.ORGANIZER)
        category = Category.objects.create(name='Test')
        event = Event.objects.create(
            organizer=organizer, category=category, title='Test',
            start_datetime=timezone.now(), end_datetime=timezone.now(),
            registration_start=timezone.now(), registration_end=timezone.now(),
            status=EventStatus.PUBLISHED
        )
        return Order.objects.create(user=customer, event=event, total=100.00)

    def test_initiate_payment(self, api_client, customer, order):
        api_client.force_authenticate(user=customer)
        url = reverse('payment-initiate')
        
        data = {
            'order_id': order.id,
            'provider': PaymentProvider.STRIPE
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'redirect_url' in response.data
        assert Payment.objects.count() == 1
        payment = Payment.objects.first()
        assert payment.provider == PaymentProvider.STRIPE
        assert payment.amount == 100.00
        
    def test_payment_webhook(self, api_client, order):
        # Create a pending payment
        payment = Payment.objects.create(
            order=order, provider=PaymentProvider.STRIPE, amount=100.00, status=PaymentStatus.PENDING
        )
        
        url = reverse('payment-webhook', kwargs={'provider': 'stripe'})
        
        payload = {
            'payment_id': str(payment.id),
            'transaction_id': 'txn_123',
            'status': 'SUCCESS'
        }
        
        response = api_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.PAID
        assert payment.transaction_id == 'txn_123'
        
        order.refresh_from_db()
        assert order.payment_status == PaymentStatus.PAID
