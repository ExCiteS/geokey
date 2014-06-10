from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from provider.oauth2.models import Client

from .base import STATUS
from .manager import ApplicationManager


class Application(models.Model):
    """
    Model for storing third-porty apllication such as mobile phone apps or
    web apps or connector modules that authorize using OAuth.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    download_url = models.URLField(blank=False)
    redirect_url = models.URLField(blank=False)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    client = models.ForeignKey(Client, null=True)

    objects = ApplicationManager()

    def delete(self):
        """
        Deletes an application by setting it's status to deleted. The record
        will not be returned from the data base.
        """
        client = Client.objects.get(pk=self.client.id)
        self.client = None
        client.delete()
        self.status = STATUS.deleted
        self.save()


@receiver(post_save, sender=Application)
def update_application_client(sender, **kwargs):
    """
    Updates the application's client information. The method is automatically
    after the application has been saved.
    """
    app = kwargs.get('instance')

    if app.client is not None:
        app.client.url = app.download_url
        app.client.redirect_uri = app.redirect_url
        app.client.save()
