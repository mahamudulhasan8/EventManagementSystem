from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from .services import OrderService
from apps.common.exceptions import ApplicationError

class OrderViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
            
        if user.role == 'ADMIN':
            return Order.objects.all()
        elif user.role == 'ORGANIZER':
            return Order.objects.filter(event__organizer=user)
        else:
            return Order.objects.filter(user=user)
            
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
        
    @extend_schema(responses={201: OrderSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = OrderService.create_order(
                user=request.user,
                event_id=serializer.validated_data['event_id'],
                items_data=serializer.validated_data['items'],
                coupon_code=serializer.validated_data.get('coupon_code')
            )
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ApplicationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
