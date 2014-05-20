from django.db import models
from django.conf import settings


class UserGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    project = models.ForeignKey('projects.Project', related_name='usergroups')
    can_contribute = models.BooleanField(default=True)


class ViewUserGroup(models.Model):
    usergroup = models.ForeignKey('UserGroup', related_name="viewgroups")
    view = models.ForeignKey('dataviews.View', related_name="usergroups")
    can_moderate = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_view = models.BooleanField(default=True)

    unique_together = ('usergroup', 'view')
