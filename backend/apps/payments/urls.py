from django.urls import path
from .views import PaymentViewSet, PaymentWebhookView

urlpatterns = [
    path('', PaymentViewSet.as_view({'post': 'create'}), name='payment-initiate'),
    path('webhook/<str:provider>/', PaymentWebhookView.as_view(), name='payment-webhook'),
]
