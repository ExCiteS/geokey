"""Command `check_confirm`."""

from pytz import utc
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from allauth.account import app_settings
from allauth.account.models import EmailAddress, EmailConfirmation


class Command(BaseCommand):
    """A command to check which users should be inactivated."""

    def set_user_inactive(self, yesterday):
        outstanding = EmailAddress.objects.filter(
            verified=False,
            user__is_active=True,
            user__is_superuser=False)

        for address in outstanding:
            try:
                confirmation = EmailConfirmation.objects.filter(
                    email_address=address).latest('id')

                if confirmation.sent < yesterday:
                    address.user.is_active = False
                    address.user.save()
            except EmailConfirmation.DoesNotExist:
                if app_settings.EMAIL_VERIFICATION in ["optional", "required"]:
                    address.user.is_active = False
                    address.user.save()

    def handle(self, *args, **options):
        now = datetime.utcnow() - timedelta(1)
        yesterday = datetime(
            now.year, now.month, now.day, 0, 0, 0).replace(tzinfo=utc)

        self.set_user_inactive(yesterday)
