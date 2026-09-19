from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel

class Role(models.TextChoices):
    ADMIN = 'ADMIN', _('Admin')
    ORGANIZER = 'ORGANIZER', _('Organizer')
    STAFF = 'STAFF', _('Staff')
    CUSTOMER = 'CUSTOMER', _('Customer')

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        
        # Default role is CUSTOMER unless specified
        extra_fields.setdefault('role', Role.CUSTOMER)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, BaseModel):
    """
    Custom user model where email is the unique identifiers
    for authentication instead of usernames.
    """
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.CUSTOMER,
        db_index=True
    )
    
    is_verified = models.BooleanField(
        _('verified'), 
        default=False,
        help_text=_('Designates whether this user has verified their email.')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    def __str__(self):
        return self.email
        
    @property
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email


class OrganizerProfile(BaseModel):
    """
    Profile for users with the ORGANIZER role.
    Stores organization-specific details.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='organizer_profile',
        limit_choices_to={'role': Role.ORGANIZER}
    )
    organization_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='organizer_logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _('organizer profile')
        verbose_name_plural = _('organizer profiles')
        
    def __str__(self):
        return self.organization_name
