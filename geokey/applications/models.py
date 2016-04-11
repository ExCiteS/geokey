"""Models for applications."""

from django.db import models

from oauth2_provider.models import AbstractApplication

from .base import STATUS
from .managers import ApplicationManager


class Application(AbstractApplication):
    """
    Represents an OAuth client an application developer resgisters with GeoKey
    in order to obtain OAuth tokens to interact with GeoKey.
    """
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    download_url = models.URLField(blank=False)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    objects = ApplicationManager()
