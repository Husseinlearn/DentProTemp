from rest_framework.permissions import BasePermission

# =====================================================================
# Standalone Pure Validator Functions (Service Layer Helpers)
# =====================================================================

def is_doctor(user) -> bool:
    """Checks if the user is an authenticated doctor/dentist."""
    return bool(
        user and 
        user.is_authenticated and 
        user.user_type == 'doctor'
    )

def is_receptionist(user) -> bool:
    """Checks if the user is an authenticated receptionist."""
    return bool(
        user and 
        user.is_authenticated and 
        user.user_type == 'receptionist'
    )

def is_manager(user) -> bool:
    """Checks if the user is an admin, manager, or superuser."""
    return bool(
        user and 
        user.is_authenticated and 
        (user.user_type in ('admin', 'manager') or user.is_superuser)
    )

# =====================================================================
# Custom DRF Permission Classes
# =====================================================================

class IsDoctor(BasePermission):
    """DRF permission wrapper for doctors."""
    def has_permission(self, request, view):
        return is_doctor(request.user)

class IsReceptionist(BasePermission):
    """DRF permission wrapper for receptionists."""
    def has_permission(self, request, view):
        return is_receptionist(request.user)

class IsManager(BasePermission):
    """DRF permission wrapper for managers and administrators."""
    def has_permission(self, request, view):
        return is_manager(request.user)
