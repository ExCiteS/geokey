"""Managers for users."""

from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom manger for geokey.user.models.User
    """
    def create_user(self, email, display_name, password=None, is_active=True,
                    **extra_fields):
        """
        Creates a new user in the data base

        Parameter
        ---------
        email : str
            Email address of the new user
        display_name : str
            display name of the new user
        password : str
            password of the new user
        is_active : Boolean
            indicates if the user is active

        Returns
        -------
        geokey.user.models.User
            The user that has been created
        """
        now = timezone.now()
        email = UserManager.normalize_email(email)

        user = self.model(email=email, display_name=display_name,
                          is_active=is_active, last_login=now, date_joined=now,
                          **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, display_name, password, **extra_fields):
        """
        Creates a new superuser

        Parameter
        ---------
        email : str
            Email address of the new user
        display_name : str
            display name of the new user
        password : str
            password of the new user

        Returns
        -------
        geokey.user.models.User
            The user that has been created
        """
        user = self.create_user(email, display_name, password=password,
                                **extra_fields)
        user.is_superuser = True
        user.save()
        return user

    def get_by_natural_key(self, username):
        """
        Returns the user identified by email. Overwrites parent method to
        make user names not case-sensitive.

        Parameter
        ---------
        username : str
            Email address to identify the user

        Returns
        -------
        geokey.user.models.User
        """
        return self.get(email__iexact=username)
