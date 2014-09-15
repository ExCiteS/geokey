from django.db import models
from django.db.models import Q
from aggregate_if import Count
from django.core.exceptions import PermissionDenied

from .base import STATUS


class ProjectQuerySet(models.query.QuerySet):
    """
    Returns the queryset of all projects that the user is allowed to access.
    """
    def for_user(self, user):
        if user.is_anonymous():
            return self.annotate(public_views=Count(
                'views', only=Q(views__isprivate=False))).filter(
                Q(status=STATUS.active) &
                Q(isprivate=False, public_views__gte=1)
                ).distinct()
        else:
            projects = self.annotate(public_views=Count(
                'views', only=Q(views__isprivate=False))).filter(

                Q(admins=user) |
                (
                    Q(status=STATUS.active) &

                    (((Q(isprivate=False) | Q(usergroups__users=user)) & (
                        Q(public_views__gte=1))) |

                        Q(usergroups__can_contribute=True,
                            usergroups__users=user) |
                        Q(usergroups__can_moderate=True,
                            usergroups__users=user) |
                        Q(usergroups__users=user,
                            usergroups__viewgroups__isnull=False))
                )
            ).distinct()
            return projects


class ProjectManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        """
        Returns the QuerySet
        """
        return ProjectQuerySet(self.model).exclude(status=STATUS.deleted)

    def get_list(self, user):
        """
        Returns a list of all projects the user is allowed to access
        """
        return self.get_query_set().for_user(user)

    def get_single(self, user, project_id):
        """
        Returns a single project or raises PermissionDenied if the user is not
        allowed to access the project.
        """
        project = self.get(pk=project_id)
        if project.can_access(user):
            return project
        else:
            raise PermissionDenied('You are not allowed to access this '
                                   'project.')

    def as_admin(self, user, project_id):
        """
        Returns the project if the user is member of the administrators group
        of raises PermissionDenied if not.
        """
        project = self.get(pk=project_id)
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
        project. Raises PermissionDenied if not.
        """
        project = self.get_single(user, project_id)
        if project.can_contribute(user):
            return project
        else:
            raise PermissionDenied('You are not eligable to contribute data '
                                   'to this project')
