from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_role


class IsProUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_pro