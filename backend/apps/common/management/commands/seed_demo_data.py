from django.core.management.base import BaseCommand
from apps.accounts.models import User, Role, OrganizerProfile
from apps.events.models import Category, Venue, Event, EventStatus
from apps.tickets.models import TicketType
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds the database with initial demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Seeding demo data...'))

        # Create Admin
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={'role': Role.ADMIN, 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('Created admin: admin@example.com / admin123')

        # Create Organizer
        org, created = User.objects.get_or_create(
            email='organizer@example.com',
            defaults={'role': Role.ORGANIZER}
        )
        if created:
            org.set_password('org123')
            org.save()
            OrganizerProfile.objects.create(
                user=org, 
                organization_name="Tech Events Co."
            )
            self.stdout.write('Created organizer: organizer@example.com / org123')

        # Create Customer
        cust, created = User.objects.get_or_create(
            email='customer@example.com',
            defaults={'role': Role.CUSTOMER}
        )
        if created:
            cust.set_password('cust123')
            cust.save()
            self.stdout.write('Created customer: customer@example.com / cust123')

        # Create Categories
        cats = ['Technology', 'Music', 'Business', 'Sports', 'Food']
        db_cats = []
        for c in cats:
            obj, _ = Category.objects.get_or_create(name=c, description=f"{c} events")
            db_cats.append(obj)
            
        # Create Venues
        v1, _ = Venue.objects.get_or_create(
            name='Convention Center', city='New York', country='USA', capacity=5000
        )
        
        # Create Events
        now = timezone.now()
        event, _ = Event.objects.get_or_create(
            title='Global Tech Summit 2026',
            defaults={
                'organizer': org,
                'category': db_cats[0],
                'venue': v1,
                'short_description': 'Biggest tech conference',
                'description': 'Join thousands of developers.',
                'start_datetime': now + timedelta(days=30),
                'end_datetime': now + timedelta(days=32),
                'registration_start': now - timedelta(days=10),
                'registration_end': now + timedelta(days=29),
                'capacity': 1000,
                'status': EventStatus.PUBLISHED,
                'is_featured': True
            }
        )
        
        if created:
            # Create Tickets
            TicketType.objects.create(
                event=event, name='General Admission', price=100.00, quantity=800
            )
            TicketType.objects.create(
                event=event, name='VIP Pass', price=500.00, quantity=200
            )
            self.stdout.write('Created Event: Global Tech Summit 2026 with tickets')
            
        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
