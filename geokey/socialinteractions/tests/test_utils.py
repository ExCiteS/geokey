"""Test for utils."""

from django.test import TestCase
from django.utils import timezone

from allauth.socialaccount.models import SocialAccount

from geokey.socialinteractions.utils import (
    start2pull,
    check_dates,
    create_new_observation,
    get_category_and_field,
    pull_from_social_media
)
from geokey.categories.tests.model_factories import CategoryFactory, TextFieldFactory

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from datetime import timedelta


class CheckDatesTest(TestCase):
    """Test for 'check_dates'."""

    def test_method(self):
        """Test method."""

        now = timezone.now()
        updated_at = now - timedelta(minutes=10)

        value_true = check_dates(updated_at, '5min')

        self.assertEqual(True, value_true)

        value_false = check_dates(updated_at, 'daily')

        self.assertNotEqual(True, value_false)


class GetCategoryAndFieldTest(TestCase):
    """Test for 'get_category_and_field'."""

    def setUp(self):
        """Set up for test method get_category_and_field."""
        self.admin = UserFactory.create()
        self.project = ProjectFactory.create(
            name="Tweets",
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.socialaccount = SocialAccount.objects.create(
            user=self.admin, provider='facebook', uid='1')
        self.category = CategoryFactory.create(
            creator=self.admin,
            project=self.project
        )

        self.field_text = TextFieldFactory.create(
            name='tweet',
            category=self.category
        )

    def test_method_when_check_when_category_and_field_exists(self):
        """Check if provides data when category and field exists."""
        tweet_cat, text_field = get_category_and_field(
            self.project,
            self.socialaccount)

        self.assertEqual(tweet_cat.id, self.category.id)
        self.assertEqual(tweet_cat.name, self.category.name)

        self.assertEqual(text_field.id, self.field_text.id)
        self.assertEqual(text_field.name, self.field_text.name)

    def test_method_when_check_when_category_and_field_does_not_exist(self):
        """Check if provides data when category and field exists."""
        self.category.delete()
        self.category.save()

        tweet_cat, text_field = get_category_and_field(
            self.project,
            self.socialaccount)

        self.assertNotEqual(tweet_cat.id, self.category.id)
        self.assertNotEqual(tweet_cat.name, self.category.name)

        self.assertNotEqual(text_field.id, self.field_text.id)
        self.assertNotEqual(text_field.name, self.field_text.name)
