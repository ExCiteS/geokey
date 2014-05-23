from django.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from projects.models import Project

from .base import STATUS


class ViewQuerySet(models.query.QuerySet):
    def for_user(self, user):
        if user.is_anonymous():
            return self.filter(isprivate=False)
        else:
            return self.filter(Q(isprivate=False) | Q(project__admins=user) |
                               Q(usergroups__usergroup__users=user)).distinct()


class ViewManager(models.Manager):
    def get_query_set(self):
        return ViewQuerySet(self.model).exclude(status=STATUS.deleted)

    def for_user(self, user):
        return self.get_query_set().for_user(user)

    def get_list(self, user, project_id):
        project = Project.objects.get_single(user, project_id)
        return project.views.for_user(user)

    def get_single(self, user, project_id, view_id):
        project = Project.objects.get_single(user, project_id)
        view = project.views.get(pk=view_id)
        if view.status == STATUS.active and (
            project.is_admin(user) or not view.isprivate or (
                not user.is_anonymous() and
                view.usergroups.filter(usergroup__users=user).exists())):
            return view
        else:
            raise PermissionDenied('You are not allowed to access this view.')

    def as_admin(self, user, project_id, view_id):
        project = Project.objects.as_admin(user, project_id)
        return project.views.get(pk=view_id)


class RuleManager(models.Manager):
    def get_query_set(self):
        return super(RuleManager, self).get_query_set().exclude(
            status=STATUS.deleted)
