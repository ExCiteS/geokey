from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver

from oauth2_provider.models import AccessToken

from .manager import UserManager


class User(AbstractBaseUser):
    """
    A user registered in the platform.
    """
    email = models.EmailField(unique=True)
    display_name = models.CharField(
        max_length=50,
        unique=True
    )
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'display_name'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def reset_password(self, password):
        """
        Resets the users password and deletes all access tokens assigned to the
        user.

        Parameters
        ----------
        password : str
            New password of the user
        """
        self.set_password(password)
        self.save()
        AccessToken.objects.filter(user=self).delete()


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


@receiver(pre_save, sender=UserGroup)
def update_application_client(sender, **kwargs):
    """
    Receiver function to ensure that can_contribute is set to True when the
    user groups has moderation permissions.
    """
    group = kwargs.get('instance')

    if group.can_moderate:
        group.can_contribute = True


class GroupingUserGroup(models.Model):
    """
    The relation between user groups and views. Used to grant permissions on
    the given view to users.
    """
    usergroup = models.ForeignKey('UserGroup', related_name='viewgroups')
    grouping = models.ForeignKey(
        'datagroupings.Grouping',
        related_name='usergroups'
    )
    can_read = models.BooleanField(default=True)
    can_view = models.BooleanField(default=True)

    unique_together = ('usergroup', 'grouping')
