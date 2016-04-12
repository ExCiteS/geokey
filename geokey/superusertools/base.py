"""Base for superuser tools."""

from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):
    """A permission to check if user is a superuser."""

    def has_permission(self, request, view):
        """
        Check if user is a superuser.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        view : rest_framework.views.APIView
            View that called the permission.

        Returns
        -------
        Boolean
            Indicating if user is a superuser.
        """
        return request.user and request.user.is_superuser
