from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response

from projects.models import Project, UserGroup


def handle_exceptions(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionDenied, err:
            return Response(str(err), status=status.HTTP_403_FORBIDDEN)
        except (
            Project.DoesNotExist,
            UserGroup.DoesNotExist,
            User.DoesNotExist
        ) as err:
            return Response(str(err), status=status.HTTP_404_NOT_FOUND)

    return wrapped
