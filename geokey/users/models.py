"""Managers for users."""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.dispatch import receiver

from simple_history.models import HistoricalRecords

from django_pgjson.fields import JsonBField
from oauth2_provider.models import AccessToken
from allauth.account.signals import email_confirmed

from geokey.core.mixins import FilterMixin
from .managers import UserManager


class User(AbstractBaseUser):
    """
    A user registered in the platform.
    """
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user is already registered with this email address.'
        }
    )
    display_name = models.CharField(
        max_length=50,
        unique=True,
        error_messages={
            'unique': 'A user is already registered with this display name.'
        }
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


@receiver(email_confirmed)
def set_user_active(sender, **kwargs):
    email_address = kwargs.get('email_address')
    email_address.user.is_active = True
    email_address.user.save()


class UserGroup(FilterMixin, models.Model):
    """
    A user gropup assigned to a project.
    """
    objects = None
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    project = models.ForeignKey('projects.Project', related_name='usergroups')
    can_contribute = models.BooleanField(default=True)
    can_moderate = models.BooleanField(default=False)
    filters = JsonBField(blank=True, null=True)
    where_clause = models.TextField(blank=True, null=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        """
        Overwrites save to implement integrity ensurance.
        """
        if self.can_moderate:
            self.can_contribute = True

        super(UserGroup, self).save(*args, **kwargs)
