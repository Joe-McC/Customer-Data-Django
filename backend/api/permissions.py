# api/permissions.py
from rest_framework import permissions

class IsOrganizationAdmin(permissions.BasePermission):
    """
    Custom permission to only allow organization admins to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class IsOrganizationMember(permissions.BasePermission):
    """
    Custom permission to only allow members of the same organization to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated