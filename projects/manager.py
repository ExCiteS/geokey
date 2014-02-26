from django.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .base import STATUS


class ProjectQuerySet(models.query.QuerySet):
    def for_user(self, user, pk=None):
        return self.filter(
            Q(admins__users=user) |
            (
                Q(status=STATUS.active) &
                (Q(isprivate=False) | Q(contributors__users=user))
            )
        ).distinct()


class ProjectManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return ProjectQuerySet(self.model).exclude(status=STATUS.deleted)

    def all(self, user):
        return self.get_query_set().for_user(user)

    def get(self, user, pk):
        project = super(ProjectManager, self).get(pk=pk)
        if user in project.admins.users.all() or (
            (not project.isprivate or user in project.contributors.users.all())
            and project.status != STATUS.inactive
        ):
            return project
        else:
            raise PermissionDenied('Not allowed')

    def as_admin(self, user, pk):
        project = super(ProjectManager, self).get(pk=pk)
        if user in project.admins.users.all():
            return project
        else:
            raise PermissionDenied('Not allowed')
