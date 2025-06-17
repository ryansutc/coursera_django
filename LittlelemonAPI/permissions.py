from rest_framework.permissions import BasePermission


class IsManagerUser(BasePermission):
    """
    Allows access only to users in the 'manager' group.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="manager").exists()
        )


class IsDeliveryUser(BasePermission):
    """
    Allows access only to users in the 'delivery' group.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="delivery").exists()
        )
