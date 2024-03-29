from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Access for changing an item only for author."""
    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated):
            return True

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author
                or request.user.is_staff)
