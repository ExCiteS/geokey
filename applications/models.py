from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from oauth2_provider.models import AbstractApplication, Application as Client

from .base import STATUS
from .manager import ApplicationManager


class Application(AbstractApplication):
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    download_url = models.URLField(blank=False)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    objects = ApplicationManager()
