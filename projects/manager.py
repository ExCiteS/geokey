from django.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .base import STATUS


class ProjectQuerySet(models.query.QuerySet):
    def for_user(self, user):
        return self.filter(
            Q(admins__users=user) |
            (
                Q(status=STATUS.active) &
                (Q(isprivate=False) | Q(contributors__users=user) |
                (self.views.filter(viewgroups__users=user).count() > 0))
            )
        ).distinct()


class ProjectManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return ProjectQuerySet(self.model).exclude(status=STATUS.deleted)

    def get_list(self, user):
        return self.get_query_set().for_user(user)

    def get_single(self, user, pk):
        project = super(ProjectManager, self).get(pk=pk)
        if project.can_access(user):
            return project
        else:
            raise PermissionDenied('You are not allowed to access this '
                                   'project.')

    def as_admin(self, user, pk):
        project = super(ProjectManager, self).get(pk=pk)
        if project.is_admin(user):
            return project
        else:
            raise PermissionDenied('You are not member of the administrators '
                                   'group of this project and therefore not '
                                   'allowed to alter the settings of the '
                                   'project')
