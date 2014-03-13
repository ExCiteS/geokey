from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response

from projects.models import Project, UserGroup
from observationtypes.models import ObservationType, Field, LookupValue
from dataviews.models import View, ViewGroup
from applications.models import Application


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
            ViewGroup.DoesNotExist,
            Application.DoesNotExist
        ) as error:
            return {"error": str(error), "head": "Not found."}

    return wrapped


def handle_exceptions_for_ajax(func):
    def wrapped(*args, **kwargs):
        # Check if user is logged in
        if args[1].user.is_anonymous():
            return Response(
                {"error": "You are not logged in. We were unable to " +
                    "authorise your request"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            return func(*args, **kwargs)
        except PermissionDenied, error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_403_FORBIDDEN
            )
        except (
            Project.DoesNotExist,
            UserGroup.DoesNotExist,
            User.DoesNotExist,
            ObservationType.DoesNotExist,
            Field.DoesNotExist,
            LookupValue.DoesNotExist,
            View.DoesNotExist,
            ViewGroup.DoesNotExist,
            Application.DoesNotExist
        ) as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_404_NOT_FOUND
            )

    return wrapped