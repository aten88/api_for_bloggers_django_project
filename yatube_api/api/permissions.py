from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Custom permission for safety requests"""
    def has_permission(self, request, view):
        """Allow GET, HEAD, OPTIONS requests or authenticated users."""
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Allow only the author to edit and delete the object."""
        return request.method in SAFE_METHODS or obj.author == request.user
