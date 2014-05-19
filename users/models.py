from django.db import models
from django.conf import settings


class UserGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    project = models.ForeignKey('projects.Project', related_name='usergroups')
    can_contribute = models.BooleanField(default=True)
