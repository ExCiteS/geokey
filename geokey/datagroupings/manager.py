from django.db import models
from django.db.models import Q

from geokey.projects.models import Project

from .base import STATUS


class GroupingQuerySet(models.query.QuerySet):
    """
    Queryset Manager for DataGroupings model
    """
    def for_user(self, user):
        """
        Returns all groupings accessable by the user.

        Parameter
        ---------
        user : geokey.users.models.User
            User the groupings are queried for

        Returns
        -------
        django.db.models.query.QuerySet
            List of data groupings
        """
        if user.is_anonymous():
            return self.filter(
                status='active', isprivate=False, project__isprivate=False)
        else:
            return self.filter(Q(status='active') & (
                               Q(isprivate=False, project__isprivate=False) |
                               Q(project__admins=user) |
                               Q(usergroups__usergroup__users=user))
                               ).distinct()


class GroupingManager(models.Manager):
    def get_queryset(self):
        """
        Returns all groupings excluding those with status deleted.

        Returns
        -------
        django.db.models.query.QuerySet
            List of data groupings
        """
        return GroupingQuerySet(self.model).exclude(status=STATUS.deleted)

    def for_user(self, user):
        """
        Returns all groupings accessable by the user.

        Parameter
        ---------
        user : geokey.users.models.User
            User the groupings are queried for

        Returns
        -------
        django.db.models.query.QuerySet
            List of data groupings
        """
        return self.get_queryset().for_user(user)

    def get_list(self, user, project_id):
        """
        Returns all groupings accessable by the user in the given project.

        Parameter
        ---------
        user : geokey.users.models.User
            User the groupings are queried for
        project_id : int
            identifies the project in the database

        Returns
        -------
        django.db.models.query.QuerySet
            List of data groupings
        """
        project = Project.objects.get_single(user, project_id)
        return project.groupings.for_user(user)

    def get_single(self, user, project_id, grouping_id):
        """
        Returns a single groupings from the given project, if accessable by the
        user.

        Parameter
        ---------
        user : geokey.users.models.User
            User the grouping is queried for
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        geokey.datagroupings.models.DataGrouping
        """
        return self.get_list(user, project_id).get(pk=grouping_id)

    def as_admin(self, user, project_id, grouping_id):
        """
        Returns a single groupings from the given project, if the user is admin
        of the project.

        Parameter
        ---------
        user : geokey.users.models.User
            User the grouping is queried for
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        geokey.datagroupings.models.DataGrouping
        """
        project = Project.objects.as_admin(user, project_id)
        return project.groupings.get(pk=grouping_id)


class RuleManager(models.Manager):
    """
    Queryset Manager for Rule model
    """
    def get_queryset(self):
        """
        Returns all rules excluding deleted ones.

        Returns
        -------
        django.db.models.query.QuerySet
            List of rules
        """
        return super(RuleManager, self).get_queryset().exclude(
            status=STATUS.deleted)
