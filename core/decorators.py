from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response

from core.exceptions import MalformedRequestData
from projects.models import Project, UserGroup
from observationtypes.models import ObservationType, Field, LookupValue
from dataviews.models import View, ViewGroup, Rule
from applications.models import Application
from contributions.models import Observation, Location, Comment


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
            Rule.DoesNotExist,
            Application.DoesNotExist
        ) as error:
            return {"error": str(error), "head": "Not found."}

    return wrapped


def handle_exceptions_for_ajax(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionDenied, error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError, error:
            return Response(
                {"error": error.messages},
                status=status.HTTP_400_BAD_REQUEST
            )
        except MalformedRequestData, error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
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
            Application.DoesNotExist,
            Observation.DoesNotExist,
            Location.DoesNotExist,
            Comment.DoesNotExist
        ) as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_404_NOT_FOUND
            )

    return wrapped
