from django.db import models
from django.conf import settings

from provider.oauth2.models import Client

from .base import STATUS
from .manager import ApplicationManager


class Application(models.Model):
    """
    Model for storing third-aorty apllication such as mobile phine apps or
    web apps or connector modules that authorize using oauth
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    download_url = models.URLField(blank=False)
    redirect_url = models.URLField(blank=False)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    client = models.ForeignKey(Client)

    objects = ApplicationManager()

    def delete(self):
        """
        Deletes an application bu setting it's status to deleted
        """
        self.status = STATUS.deleted
        self.save()
