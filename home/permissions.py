from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUserOrReadOnly(BasePermission):
    """
    Custom permission to only allow superusers to edit objects.
    """
    def has_permission(self, request, view):
        # Allow read-only access for all users
        if request.method in SAFE_METHODS:
            return True
        # Allow write access only for superusers
        return request.user and request.user.is_superuser
