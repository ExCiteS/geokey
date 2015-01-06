from django.db import models
from django.core.exceptions import PermissionDenied

from .base import STATUS


class ApplcationQuerySet(models.query.QuerySet):
    def for_user(self, user):
        """
        Returns all applications the given user has created.
        """
        return self.filter(creator=user)


class ApplicationManager(models.Manager):
    def get_queryset(self):
        """
        Returns all applications excluding the ones the are deleted.
        """
        return ApplcationQuerySet(self.model).exclude(status=STATUS.deleted)

    def get_list(self, user):
        """
        Returns a list of all applications that the user has created.
        """
        return self.get_queryset().for_user(user)

    def as_owner(self, user, app_id):
        """
        Returns the application if the user is the creator. Raises
        `PermissionDenied` id not.
        """
        app = self.get(pk=app_id)
        if app.creator == user:
            return app
        else:
            raise PermissionDenied('You are not the owner of this '
                                   'application and therefore not allowed '
                                   'to access this app.')
