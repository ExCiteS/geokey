from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response

from projects.models import Project, UserGroup
from observationtypes.models import ObservationType, Field, LookupValue
from views.models import View, ViewGroup


def handle_exceptions_for_admin(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionDenied, error:
            return {"error": str(error), "head": "Permission denied."}
        except (
            Project.DoesNotExist,
            ObservationType.DoesNotExist,
            Field.DoesNotExist,
            View.DoesNotExist,
            ViewGroup.DoesNotExist
        ) as error:
            return {"error": str(error), "head": "Not found."}

    return wrapped


def handle_exceptions_for_ajax(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionDenied, error:
            return Response(str(error), status=status.HTTP_403_FORBIDDEN)
        except (
            Project.DoesNotExist,
            UserGroup.DoesNotExist,
            User.DoesNotExist,
            ObservationType.DoesNotExist,
            Field.DoesNotExist,
            LookupValue.DoesNotExist,
            View.DoesNotExist,
            ViewGroup.DoesNotExist
        ) as error:
            return Response(str(error), status=status.HTTP_404_NOT_FOUND)

    return wrapped
