"""Managers for applications."""

from django.db import models
from django.core.exceptions import PermissionDenied

from .base import STATUS


class ApplcationQuerySet(models.query.QuerySet):
    """
    Adds application specific queryset methods.
    """
    def for_user(self, user):
        """Returns all applications the given user has created.

        Parameters
        ----------
        user : ``geokey.users.models.User``
            The user applications are queried for

        Returns
        -------
        ``django.db.models.Queryset``
            All user's applications
        """
        return self.filter(user=user)


class ApplicationManager(models.Manager):
    """
    Adds application specific manager functions.
    """

    def get_queryset(self):
        """
        Returns all applications excluding the ones the are deleted.

        Returns
        -------
        ``django.db.models.Queryset``
            All applications
        """
        return ApplcationQuerySet(self.model).exclude(status=STATUS.deleted)

    def get_list(self, user):
        """
        Returns a list of all applications that the user has created.

        Parameters
        ----------
        user : ``geokey.users.models.User``
            The user applications are queried for

        Returns
        -------
        ``django.db.models.Queryset``
            All user's applications
        """
        return self.get_queryset().for_user(user)

    def as_owner(self, user, app_id):
        """
        Returns a single application if the user is the creator.

        Parameters
        ----------
        user : ``geokey.users.models.User``
            The user the application is queried for
        app_id : ``int``
            ID identifying the application in the database

        Returns
        -------
        ``geokey.applications.models.Application``
            Application model intance

        Raises
        -------
        PermissionDenied
            if user is not the owner of the application.
        """
        app = self.get(pk=app_id)
        if app.user == user:
            return app
        else:
            raise PermissionDenied('You are not the owner of this '
                                   'application and therefore not allowed '
                                   'to access this app.')
