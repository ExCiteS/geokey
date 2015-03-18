from django.core.management.base import NoArgsCommand

from datetime import datetime, timedelta
from pytz import utc

from allauth.account.models import EmailAddress, EmailConfirmation


class Command(NoArgsCommand):
    def set_user_inactive(self, yesterday):
        outstanding = EmailAddress.objects.filter(verified=False)
        for address in outstanding:
            confirmation = EmailConfirmation.objects.filter(
                email_address=address
            ).latest('id')

            if confirmation.sent < yesterday:
                address.user.is_active = False
                address.user.save()

    def handle(self, *args, **options):
        now = datetime.utcnow() - timedelta(1)
        yesterday = datetime(
            now.year, now.month, now.day, 0, 0, 0).replace(tzinfo=utc)

        self.set_user_inactive(yesterday)
