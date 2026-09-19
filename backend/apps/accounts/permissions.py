from rest_framework import permissions
from .models import Role

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.ADMIN)

class IsOrganizer(permissions.BasePermission):
    """
    Allows access only to organizer users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.ORGANIZER)

class IsStaff(permissions.BasePermission):
    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.STAFF)

class IsCustomer(permissions.BasePermission):
    """
    Allows access only to customer users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.CUSTOMER)

class IsAdminOrOrganizer(permissions.BasePermission):
    """
    Allows access to admins or organizers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [Role.ADMIN, Role.ORGANIZER]
        )
