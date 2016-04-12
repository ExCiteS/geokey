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

        confirmed_email = EmailAddress.objects.create(
            user=confirmed_user,
            email=confirmed_user.email,
            verified=True
        )

        unconfirmed_email = EmailAddress.objects.create(
            user=unconfirmed_user,
            email=unconfirmed_user.email,
            verified=False
        )

        EmailConfirmation.objects.create(
            email_address=confirmed_email,
            created=datetime.utcnow().replace(tzinfo=utc),
            sent=datetime.utcnow().replace(tzinfo=utc),
            key='38974hewjkhnuweyf8h8d'
        )
        EmailConfirmation.objects.create(
            email_address=unconfirmed_email,
            created=datetime.utcnow().replace(tzinfo=utc),
            sent=datetime.utcnow().replace(tzinfo=utc),
            key='38974hewjkhnsdfuweyf8h8d'
        )

        yesterday = datetime.utcnow().replace(tzinfo=utc)
        command = CheckConfirm()
        command.set_user_inactive(yesterday)

        ref_unconfirmed = User.objects.get(pk=unconfirmed_user.id)
        self.assertFalse(ref_unconfirmed.is_active)

        ref_confirmed = User.objects.get(pk=confirmed_user.id)
        self.assertTrue(ref_confirmed.is_active)
