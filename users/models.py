from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver

from contributions.models import Observation, Comment
from projects.models import Project

from .manager import UserManager


class User(AbstractBaseUser):
    """
    A user registered in the platform.
    """
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=50)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_stats(self):
        stats = {}

        stats['observations'] = Observation.objects.filter(
            creator=self).count()
        stats['comments'] = Comment.objects.filter(creator=self).count()
        stats['projects'] = Project.objects.filter(creator=self).count()

        return stats


class UserGroup(models.Model):
    """
    A user gropup assigned to a project.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    project = models.ForeignKey('projects.Project', related_name='usergroups')
    can_contribute = models.BooleanField(default=True)
    can_moderate = models.BooleanField(default=False)
    view_all_contrib = models.BooleanField(default=True)
    read_all_contrib = models.BooleanField(default=True)


@receiver(pre_save, sender=UserGroup)
def update_application_client(sender, **kwargs):
    group = kwargs.get('instance')

    if group.can_moderate:
        group.can_contribute = True


class ViewUserGroup(models.Model):
    """
    The relation between user groups and views. Used to grant permissions on
    the given view to users.
    """
    usergroup = models.ForeignKey('UserGroup', related_name="viewgroups")
    view = models.ForeignKey('dataviews.View', related_name="usergroups")
    can_read = models.BooleanField(default=False)
    can_view = models.BooleanField(default=True)

    unique_together = ('usergroup', 'view')
