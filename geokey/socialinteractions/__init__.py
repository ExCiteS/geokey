"""Models for subsets."""

from django.conf import settings
from django.db import models


from allauth.socialaccount.models import SocialAccount


class SocialInteraction(models.Model):
    """Stores a single social interaction."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    text_to_post = models.TextField(blank=True, null=True)
    project = models.ForeignKey(
        'projects.Project',
        related_name='socialinteractions'
    )
    socialaccount = models.ForeignKey(
        SocialAccount,
        related_name='socialinteractions'
    )
