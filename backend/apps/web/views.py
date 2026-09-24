from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from apps.events.models import Event, EventStatus, Category
from apps.orders.models import Order
from apps.accounts.models import User, Role, OrganizerProfile
from apps.accounts.services import UserService, OrganizerService

def home(request):
    featured_events = Event.objects.filter(status=EventStatus.PUBLISHED, is_featured=True)[:6]
    if not featured_events.exists():
        featured_events = Event.objects.filter(status=EventStatus.PUBLISHED)[:6]
    return render(request, 'web/home.html', {'featured_events': featured_events, 'events': featured_events})

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
    if request.user.is_authenticated:
        if getattr(request.user, 'role', '') in [Role.ADMIN, Role.ORGANIZER]:
            return redirect('dashboard_home')
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember-me')

        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'auth/login.html', {'email': email})

        user = authenticate(request, email=email, password=password)
        if user is None:
            user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser session

                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)

                if getattr(user, 'role', '') in [Role.ADMIN, Role.ORGANIZER]:
                    return redirect('dashboard_home')
                return redirect('home')
            else:
                messages.error(request, 'Your account is deactivated. Please contact support.')
        else:
            messages.error(request, 'Invalid email or password. Please verify your credentials.')

        return render(request, 'auth/login.html', {'email': email})

    return render(request, 'auth/login.html')

def register_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'role', '') in [Role.ADMIN, Role.ORGANIZER]:
            return redirect('dashboard_home')
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        role = request.POST.get('role', Role.CUSTOMER).upper()
        organization_name = request.POST.get('organization_name', '').strip()

        context_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'role': role,
            'organization_name': organization_name,
        }

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'auth/register.html', context_data)

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists. Please log in.')
            return render(request, 'auth/register.html', context_data)

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'auth/register.html', context_data)

        try:
            if role == Role.ORGANIZER:
                org_title = organization_name or f"{first_name} {last_name}".strip() or f"{email.split('@')[0]} Org"
                user, _ = OrganizerService.create_organizer(
                    email=email,
                    password=password,
                    organization_name=org_title,
                    first_name=first_name,
                    last_name=last_name,
                )
            else:
                user = UserService.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=Role.CUSTOMER
                )

            user.is_active = True
            user.is_verified = True
            user.save(update_fields=['is_active', 'is_verified'])

            login(request, user)
            messages.success(request, f'Account successfully created! Welcome, {user.first_name or user.email}.')

            if user.role in [Role.ADMIN, Role.ORGANIZER]:
                return redirect('dashboard_home')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'auth/register.html', context_data)

    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
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
