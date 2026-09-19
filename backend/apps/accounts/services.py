from django.contrib.auth import get_user_model
from django.db import transaction
from .models import OrganizerProfile, Role
from apps.common.exceptions import ApplicationError

User = get_user_model()

class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(email, password, first_name='', last_name='', phone='', role=Role.CUSTOMER):
        """
        Creates and returns a user with an email and password.
        """
        if User.objects.filter(email=email).exists():
            raise ApplicationError("User with this email already exists.")
            
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role
        )
        return user


class OrganizerService:
    @staticmethod
    @transaction.atomic
    def create_organizer(email, password, organization_name, first_name='', last_name='', phone=''):
        """
        Creates an organizer user and their profile in one atomic transaction.
        """
        user = UserService.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=Role.ORGANIZER
        )
        
        profile = OrganizerProfile.objects.create(
            user=user,
            organization_name=organization_name,
            phone=phone
        )
        
        return user, profile
