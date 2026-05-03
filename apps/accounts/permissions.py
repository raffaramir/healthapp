"""DRF and Django view permission helpers."""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework.permissions import BasePermission

from .models import Role


class IsApproved(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_approved)


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (u.is_admin_role or u.is_superuser))


class HasRole(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role in self.allowed_roles)


def role_required(*roles, require_approval=True):
    """View decorator: restrict access by role and approval status."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            if roles and user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                raise PermissionDenied
            if require_approval and not user.is_approved:
                messages.warning(
                    request,
                    'Your account is awaiting admin approval. Some features are locked.'
                )
                return redirect('dashboard:pending_approval')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def admin_required(view_func):
    return role_required(Role.ADMIN, require_approval=False)(view_func)
