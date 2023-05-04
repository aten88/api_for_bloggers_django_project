from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Custom permission for safety requests"""
    def has_permission(self, request, view):
        """Allow GET, HEAD, OPTIONS requests or authenticated users."""
        return request.method

    def has_object_permission(self, request, view, obj):
        """Allow only the author to edit and delete the object."""
        return request.method in SAFE_METHODS or obj.author == request.user
