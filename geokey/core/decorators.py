"""Core decorators."""

from django.core.exceptions import PermissionDenied, ValidationError

from rest_framework import status
from rest_framework.response import Response

from geokey.core.exceptions import (
    MalformedRequestData,
    Unauthenticated,
    FileTypeError
)
from geokey.projects.models import Project
from geokey.users.models import User, UserGroup
from geokey.categories.models import (
    Category, Field, LookupValue, MultipleLookupValue
)
from geokey.applications.models import Application
from geokey.contributions.models import (
    Observation, Comment, Location, MediaFile
)
from geokey.subsets.models import Subset


def handle_exceptions_for_admin(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionDenied, error:
            return {
                "error_description": str(error),
                "error": "Permission denied."
            }
        except (
            Project.DoesNotExist,
            Subset.DoesNotExist,
            Category.DoesNotExist,
            Field.DoesNotExist,
            Application.DoesNotExist
        ) as error:
            return {"error_description": str(error), "error": "Not found."}

    return wrapped


def handle_exceptions_for_ajax(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Unauthenticated, error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_401_UNAUTHORIZED
            )
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
        except (MalformedRequestData, FileTypeError), error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (
            Project.DoesNotExist,
            UserGroup.DoesNotExist,
            User.DoesNotExist,
            Category.DoesNotExist,
            Field.DoesNotExist,
            MultipleLookupValue.DoesNotExist,
            LookupValue.DoesNotExist,
            Application.DoesNotExist,
            Observation.DoesNotExist,
            Location.DoesNotExist,
            Comment.DoesNotExist,
            MediaFile.DoesNotExist
        ) as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_404_NOT_FOUND
            )

    return wrapped
