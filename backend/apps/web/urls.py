from django.urls import path
from . import views

urlpatterns = [
    # Public Frontend
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/events/', views.dashboard_events, name='dashboard_events'),
    path('dashboard/bookings/', views.dashboard_bookings, name='dashboard_bookings'),
]
