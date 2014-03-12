from django.db import models
from django.core.exceptions import PermissionDenied

from provider.oauth2.models import Client

from .base import STATUS


class ApplcationQuerySet(models.query.QuerySet):
    def for_user(self, user):
        return self.filter(creator=user)


class ApplicationManager(models.Manager):
    def create(self, **kwargs):
        creator = kwargs.get('creator')
        name = kwargs.get('name')
        url = kwargs.get('download_url')
        redirect_url = kwargs.get('redirect_url')

        client = Client.objects.create(user=creator, name=name, client_type=0,
                                       url=url, redirect_uri=redirect_url)

        return super(ApplicationManager, self).create(client=client, **kwargs)

    def get_query_set(self):
        return ApplcationQuerySet(self.model).exclude(status=STATUS.deleted)

    def get_list(self, user):
        return self.get_query_set().for_user(user)

    def get_single(self, user, app_id):
        app = self.get(pk=app_id)
        if app.creator == user:
            return app
        else:
            raise PermissionDenied('You are not the creator of this '
                                   'application and therefore not allowed '
                                   'to access this app.')
