from django.urls import path
from .views import CheckInView

urlpatterns = [
    path('scan/', CheckInView.as_view(), name='ticket-scan'),
]
