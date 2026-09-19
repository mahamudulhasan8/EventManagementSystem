from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from apps.common.models import BaseModel
from apps.accounts.models import User

class EventStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    PUBLISHED = 'PUBLISHED', _('Published')
    ONGOING = 'ONGOING', _('Ongoing')
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELLED = 'CANCELLED', _('Cancelled')

class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Venue(BaseModel):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='venues/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"

class Event(BaseModel):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events', limit_choices_to={'role': 'ORGANIZER'})
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.TextField(max_length=500)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='events/covers/', null=True, blank=True)
    
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum total capacity for this event.")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.DRAFT)
    is_featured = models.BooleanField(default=False)
    terms = models.TextField(blank=True)

    class Meta:
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['status', 'start_datetime']),
            models.Index(fields=['organizer', 'status']),
            models.Index(fields=['slug']),
        ]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            # We add uuid part to prevent slug collision for common names
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{str(self.id)[:8]}" if self.id else base_slug
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Speaker(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='speakers')
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='events/speakers/', null=True, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.event.title})"


class EventSession(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    speaker = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    room = models.CharField(max_length=100, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['start_time', 'sort_order']
        
    def __str__(self):
        return f"{self.title} - {self.event.title}"
