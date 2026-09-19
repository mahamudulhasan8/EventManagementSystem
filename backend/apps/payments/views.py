from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .models import Payment, PaymentProvider
from apps.orders.models import Order
from .services import PaymentService

class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    provider = serializers.ChoiceField(choices=PaymentProvider.choices)

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=InitiatePaymentSerializer,
        responses={200: inline_serializer(
            name='PaymentInitiateResponse',
            fields={
                'payment_id': serializers.UUIDField(),
                'provider': serializers.CharField(),
                'redirect_url': serializers.URLField()
            }
        )}
    )
    def create(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = Order.objects.get(
                id=serializer.validated_data['order_id'], 
                user=request.user
            )
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            init_data = PaymentService.initiate_payment(
                order=order, 
                provider=serializer.validated_data['provider']
            )
            return Response(init_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PaymentWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(exclude=True)
    def post(self, request, provider):
        """
        Generic webhook endpoint. Ex: /api/v1/payments/webhook/stripe/
        """
        # Validate provider
        if provider.upper() not in [p.value for p in PaymentProvider]:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        # In a real app, you would verify the webhook signature here
        
        success = PaymentService.process_webhook(provider.upper(), request.data)
        
        if success:
            return Response({"status": "processed"})
        return Response({"status": "failed or ignored"}, status=status.HTTP_400_BAD_REQUEST)
