from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from provider.oauth2.models import Client

from .base import STATUS
from .manager import ApplicationManager


class Application(models.Model):
    """
    Model for storing third-aorty apllication such as mobile phine apps or
    web apps or connector modules that authorize using oauth.
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
    client = models.ForeignKey(Client, null=True)

    objects = ApplicationManager()

    def delete(self):
        """
        Deletes an application by setting it's status to deleted.
        """
        self.status = STATUS.deleted
        self.save()


@receiver(post_save, sender=Application)
def update_application_client(sender, **kwargs):
    app = kwargs.get('instance')

    if app.client is not None:
        app.client.url = app.download_url
        app.client.redirect_uri = app.redirect_url
        app.client.save()

    if app.status == STATUS.active and app.client is None:
        app.client = Client.objects.create(
            user=app.creator,
            name=app.name,
            client_type=0,
            url=app.download_url,
            redirect_uri=app.redirect_url
        )
        app.save()

    if ((app.status == STATUS.deleted or app.status == STATUS.inactive)
            and app.client is not None):
        client = Client.objects.get(pk=app.client.id)
        app.client = None
        app.save()
        client.delete()
