from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


class RoleBasedWritePermission(BasePermission):
    message = 'You do not have permission to modify this resource.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.is_superuser or user.role in {User.Role.ADMIN, User.Role.TEACHER}