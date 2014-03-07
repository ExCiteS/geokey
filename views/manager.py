from django.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from projects.models import Project

from .base import STATUS


class ViewQuerySet(models.query.QuerySet):
    def for_user(self, user):
        return self.filter(Q(project__admins__users=user) |
                           Q(usergroups__users=user)).distinct()


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
        if (project.is_admin(user) or
                view.usergroups.filter(users=user).count() > 0):
            return view
        else:
            raise PermissionDenied('You are not allowrd to access this view.')

    def as_admin(self, user, project_id, view_id):
        project = Project.objects.as_admin(user, project_id)
        return project.views.get(pk=view_id)
