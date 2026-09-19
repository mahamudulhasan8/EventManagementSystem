from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from apps.events.models import Event, EventStatus, Category
from apps.orders.models import Order
from apps.accounts.models import User

def home(request):
    featured_events = Event.objects.filter(status=EventStatus.PUBLISHED, is_featured=True)[:3]
    upcoming_events = Event.objects.filter(status=EventStatus.PUBLISHED).order_by('start_datetime')[:6]
    
    featured_events = Event.objects.filter(status='PUBLISHED')[:6]
    return render(request, 'web/home.html', {'events': featured_events})

def event_list(request):
    events = Event.objects.filter(status='PUBLISHED')
    categories = Category.objects.all()
    return render(request, 'web/events.html', {'events': events, 'categories': categories})

def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'web/event_detail.html', {'event': event})

@login_required
def my_bookings(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'web/my_bookings.html', {'orders': orders})

def login_view(request):
    return render(request, 'auth/login.html')

def register_view(request):
    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def dashboard_home(request):
    user = request.user
    context = {}
    
    # Mock user data if not logged in (for demo purposes)
    if not user.is_authenticated:
        context['total_events'] = 5
        class MockUser:
            first_name = "Admin"
            email = "admin@example.com"
        context['user'] = MockUser()
    else:
        if hasattr(user, 'role') and (user.role == 'ORGANIZER' or user.role == 'ADMIN'):
            context['total_events'] = Event.objects.filter(organizer=user).count() if user.role == 'ORGANIZER' else Event.objects.count()
            
    return render(request, 'dashboard/home.html', context)

def dashboard_events(request):
    # Mock user data if not logged in (for demo purposes)
    events = Event.objects.all() if not request.user.is_authenticated or request.user.role == 'ADMIN' else Event.objects.filter(organizer=request.user)
    return render(request, 'dashboard/events.html', {'events': events})

def dashboard_bookings(request):
    orders = Order.objects.all()[:20]
    return render(request, 'dashboard/bookings.html', {'orders': orders})
