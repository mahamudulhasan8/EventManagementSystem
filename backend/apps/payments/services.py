from apps.orders.models import Order, OrderStatus, PaymentStatus
from .models import Payment, PaymentProvider
from django.db import transaction
import uuid

class PaymentService:
    @staticmethod
    def initiate_payment(order, provider):
        """
        Creates a payment record and returns gateway initiation data.
        In a real application, this would call the respective gateway's SDK or API.
        """
        if order.payment_status == PaymentStatus.PAID:
            raise ValueError("Order is already paid.")
            
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'provider': provider,
                'amount': order.total,
                'currency': 'BDT' if provider != PaymentProvider.STRIPE else 'USD',
                'status': PaymentStatus.PENDING
            }
        )
        
        # If payment exists but provider is different, update provider
        if not created and payment.provider != provider:
            payment.provider = provider
            payment.currency = 'BDT' if provider != PaymentProvider.STRIPE else 'USD'
            payment.save()
            
        # Simulate gateway initialization response
        redirect_url = f"https://sandbox.gateway.com/pay/{uuid.uuid4()}"
        
        # Real logic would be:
        # if provider == PaymentProvider.STRIPE:
        #     return StripeService().create_checkout_session(payment)
        # elif provider == PaymentProvider.SSLCOMMERZ:
        #     return SSLCommerzService().init_payment(payment)
        # ... and so on
        
        return {
            "payment_id": payment.id,
            "provider": provider,
            "redirect_url": redirect_url
        }

    @staticmethod
    @transaction.atomic
    def process_webhook(provider, payload):
        """
        Process the webhook/callback from the payment gateway.
        """
        # Simulated extraction of transaction info
        transaction_id = payload.get('transaction_id')
        payment_id = payload.get('payment_id')
        status_str = payload.get('status')
        
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return False
            
        if status_str == 'SUCCESS':
            payment.status = PaymentStatus.PAID
            payment.transaction_id = transaction_id
            payment.gateway_response = payload
            payment.save()
            
            # Update Order
            order = payment.order
            order.payment_status = PaymentStatus.PAID
            order.status = OrderStatus.CONFIRMED
            order.save()
            
            # Generate Tickets logic goes here (e.g. signal or direct call)
            from apps.attendees.services import AttendeeService
            AttendeeService.generate_tickets_for_order(order)
            
            return True
        elif status_str in ['FAILED', 'CANCELLED']:
            payment.status = PaymentStatus.FAILED
            payment.gateway_response = payload
            payment.save()
            
            order = payment.order
            order.payment_status = PaymentStatus.FAILED
            order.save()
            
        return False
