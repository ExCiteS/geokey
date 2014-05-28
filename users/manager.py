from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, display_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        if not display_name:
            raise ValueError('The given display name must be set')

        now = timezone.now()
        email = UserManager.normalize_email(email)

        user = self.model(email=email, display_name=display_name,
                          is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user
