from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )
        

class IsSystemAdmin(BasePermission):
    """
    Allows access only to users marked as admin in the system.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_admin", False)
        )
        

class IsNormalUser(BasePermission):
    """
    Allows access only to authenticated non-admin users.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not getattr(request.user, "is_admin", False)
        )


