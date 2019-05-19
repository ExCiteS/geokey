"""Tests for commands of users."""

from pytz import utc
from datetime import datetime

from django.test import TestCase

from allauth.account.models import EmailAddress, EmailConfirmation

from ..models import User
from ..management.commands.check_confirm import Command as CheckConfirm
from ..tests.model_factories import UserFactory


class CheckConfirmTest(TestCase):
    def test_check_confirm(self):
        confirmed_user = UserFactory.create()
        unconfirmed_user = UserFactory.create()
        unconfirmed_user_without_confirmation = UserFactory.create()
        inactive_user = UserFactory.create(**{'is_active': True})
        unconfirmed_superuser = UserFactory.create(**{'is_superuser': True})

        confirmed_user_email = EmailAddress.objects.create(
            user=confirmed_user,
            email=confirmed_user.email,
            verified=True
        )
        unconfirmed_user_email = EmailAddress.objects.create(
            user=unconfirmed_user,
            email=unconfirmed_user.email,
            verified=False
        )
        unconfirmed_inactive_email = EmailAddress.objects.create(
            user=inactive_user,
            email=inactive_user.email,
            verified=False
        )
        unconfirmed_superuser_email = EmailAddress.objects.create(
            user=unconfirmed_superuser,
            email=unconfirmed_superuser.email,
            verified=False
        )

        # Edge case - email confirmation was not sent
        EmailAddress.objects.create(
            user=unconfirmed_user_without_confirmation,
            email=unconfirmed_user_without_confirmation.email,
            verified=False
        )

        EmailConfirmation.objects.create(
            email_address=confirmed_user_email,
            created=datetime.utcnow().replace(tzinfo=utc),
            sent=datetime.utcnow().replace(tzinfo=utc),
            key='a0qzf3xwn420gdbv2d1v'
        )
        EmailConfirmation.objects.create(
            email_address=unconfirmed_user_email,
            created=datetime.utcnow().replace(tzinfo=utc),
            sent=datetime.utcnow().replace(tzinfo=utc),
            key='16fy83dz7ucb6p8ogsc8'
        )
        EmailConfirmation.objects.create(
            email_address=unconfirmed_inactive_email,
            created=datetime.utcnow().replace(tzinfo=utc),
            sent=datetime.utcnow().replace(tzinfo=utc),
            key='qogd4jgvu7x7zi1eic2x'
        )
        EmailConfirmation.objects.create(
            email_address=unconfirmed_inactive_email,
            created=datetime.utcnow().replace(tzinfo=utc),
            sent=datetime.utcnow().replace(tzinfo=utc),
            key='ei8n5addsmu5igtvgie1'
        )
        EmailConfirmation.objects.create(
            email_address=unconfirmed_superuser_email,
            created=datetime.utcnow().replace(tzinfo=utc),
            sent=datetime.utcnow().replace(tzinfo=utc),
            key='5g3ovaztqun1b8c7wgjn'
        )

        yesterday = datetime.utcnow().replace(tzinfo=utc)
        command = CheckConfirm()
        command.set_user_inactive(yesterday)

        confirmed_user.refresh_from_db()
        self.assertTrue(confirmed_user.is_active)
        unconfirmed_user.refresh_from_db()
        self.assertFalse(unconfirmed_user.is_active)
        unconfirmed_user_without_confirmation.refresh_from_db()
        self.assertFalse(unconfirmed_user_without_confirmation.is_active)
        inactive_user.refresh_from_db()
        self.assertFalse(inactive_user.is_active)
        unconfirmed_superuser.refresh_from_db()
        self.assertTrue(unconfirmed_superuser.is_active)
