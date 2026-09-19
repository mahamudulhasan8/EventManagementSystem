from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, OrganizerProfile, Role

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_verified', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        (_('Role & Status'), {'fields': ('role', 'is_verified')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'role', 'is_verified'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')

@admin.register(OrganizerProfile)
class OrganizerProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'user_email', 'phone', 'created_at')
    search_fields = ('organization_name', 'user__email', 'phone')
    list_select_related = ('user',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
