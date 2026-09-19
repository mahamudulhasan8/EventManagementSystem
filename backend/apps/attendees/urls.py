from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendeeViewSet

router = DefaultRouter()
router.register(r'attendees', AttendeeViewSet, basename='attendee')

urlpatterns = [
    path('', include(router.urls)),
]
