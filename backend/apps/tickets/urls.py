from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketTypeViewSet

router = DefaultRouter()
router.register(r'ticket-types', TicketTypeViewSet, basename='ticket-type')

urlpatterns = [
    path('', include(router.urls)),
]
