from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Custom permission for safety requests"""
    def has_object_permission(self, request, view, obj):
        """Checked requests"""
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE' and obj.author != request.user:
            return False
        return obj.author == request.user
