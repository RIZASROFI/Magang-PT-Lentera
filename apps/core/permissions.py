"""
Custom Permission Classes
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission untuk:
    - Admin/Staff: Dapat melakukan CRUD (POST, PUT, PATCH, DELETE)
    - User Biasa: Hanya dapat membaca (GET)
    """
    
    def has_permission(self, request, view):
        # User harus authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # GET requests diperbolehkan untuk semua user yang authenticated
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Untuk POST, PUT, PATCH, DELETE hanya admin/staff yang diperbolehkan
        return request.user.is_staff or request.user.is_superuser


class IsAdmin(permissions.BasePermission):
    """
    Permission hanya untuk admin/staff
    """
    
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)
