"""Managers for projects."""

from django.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .base import STATUS


class ProjectQuerySet(models.query.QuerySet):
    """
    Custom QuerySet for geokey.projects.models.Project
    """
    def for_user(self, user):
        """
        Returns the projects for the user.

        For anonymous users:
            Returns all projects that are public and have at least one public
            data grouping.

        For authenticated users:
            Returns all projects that
                - are public
                - all projects the user can contribute or moderate

        Parameter
        ---------
        user : geokey.users.models.User
            User projects are queried for

        Return
        ------
        django.db.models.query.QuerySet
            List of geokey.projects.models.Project
        """
        if user.is_anonymous():
            return self.filter(
                    Q(status=STATUS.active) & Q(isprivate=False)
                ).distinct()
        else:
            projects = (self
                        .filter(
                            Q(admins=user) |
                            (
                                Q(status=STATUS.active) &
                                (
                                    Q(isprivate=False) |
                                    Q(usergroups__users=user)
                                )
                            )
                        ).distinct())

            return projects


class ProjectManager(models.Manager):
    """
    Custom Manager for geokey.projects.models.Project
    """
    use_for_related_fields = True

    def get_queryset(self):
        """
        Returns the QuerySet excluding deleted projects

        Returns
        -------
        django.db.models.query.QuerySet
            List of geokey.projects.models.Project
        """
        return (ProjectQuerySet(self.model)
                .prefetch_related('admins')
                .select_related('creator')
                .exclude(status=STATUS.deleted))

    def get_list(self, user):
        """
        Returns a list of all projects the user is allowed to access

        Parameter
        ---------
        user : geokey.users.models.User
            User projects are queried for

        Return
        ------
        django.db.models.query.QuerySet
            List of geokey.projects.models.Project
        """
        return self.get_queryset().for_user(user)

    def get_single(self, user, project_id):
        """
        Returns a single project or raises PermissionDenied if the user is not
        allowed to access the project.

        Parameter
        ---------
        user : geokey.users.models.User
            User projects are queried for
        project_id : int
            identifies the project in the database

        Return
        ------
        geokey.projects.models.Project
        """
        return self.get_list(user).get(pk=project_id)

    def as_admin(self, user, project_id):
        """
        Returns the project if the user is member of the administrators group.

        Parameter
        ---------
        user : geokey.users.models.User
            User projects are queried for
        project_id : int
            identifies the project in the database

        Return
        ------
        geokey.projects.models.Project

        Raises
        ------
        PermissionDenied
            If user is not administrator of the project
        """
        if user.is_superuser:
            return self.get(pk=project_id)

        project = self.get_single(user, project_id)
        if project.is_admin(user):
            return project
        else:
            raise PermissionDenied('You are not member of the administrators '
                                   'group of this project and therefore not '
                                   'allowed to alter the settings of the '
                                   'project')

    def as_contributor(self, user, project_id):
        """
        Returns the project if the user is eligable to contribute data to the
        project.

        Parameter
        ---------
        user : geokey.users.models.User
            User projects are queried for
        project_id : int
            identifies the project in the database

        Return
        ------
        geokey.projects.models.Project

        Raises
        ------
        PermissionDenied
            If user is not administrator of the project
        """
        project = self.get_single(user, project_id)
        if project.can_contribute(user):
            return project
        else:
            raise PermissionDenied('You are not eligable to contribute data '
                                   'to this project')
