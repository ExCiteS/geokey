from django.db import models
from django.core.exceptions import PermissionDenied

from .base import STATUS


class ApplcationQuerySet(models.query.QuerySet):
    def for_user(self, user):
        return self.filter(creator=user)


class ApplicationManager(models.Manager):
    def get_query_set(self):
        return ApplcationQuerySet(self.model).exclude(status=STATUS.deleted)

    def get_list(self, user):
        return self.get_query_set().for_user(user)

    def as_owner(self, user, app_id):
        app = self.get(pk=app_id)
        if app.creator == user:
            return app
        else:
            raise PermissionDenied('You are not the owner of this '
                                   'application and therefore not allowed '
                                   'to access this app.')
