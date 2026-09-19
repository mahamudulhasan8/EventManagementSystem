from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegisterCustomerView,
    RegisterOrganizerView,
    LogoutView,
    ProfileView
)

urlpatterns = [
    # JWT Auth
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Registration
    path('register/customer/', RegisterCustomerView.as_view(), name='register_customer'),
    path('register/organizer/', RegisterOrganizerView.as_view(), name='register_organizer'),
    
    # Profile
    path('me/', ProfileView.as_view(), name='my_profile'),
]
