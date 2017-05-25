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
from geokey.socialinteractions.tests.models_factories import SocialInteractionPullFactory
from geokey.contributions.models import Observation

from datetime import timedelta, datetime


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
        self.project = ProjectFactory.create(creator=self.admin)

        self.socialaccount = SocialAccount.objects.create(
            user=self.admin, provider='facebook', uid='1')
        self.category = CategoryFactory.create(
            name='Tweets',
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
        self.assertEqual(tweet_cat.name, self.category.name)

        self.assertNotEqual(text_field.id, self.field_text.id)
        self.assertEqual(text_field.name, self.field_text.name)


class CreateNewObservationTest(TestCase):
    """test for method 'create_new_observation'."""

    def setup(self):
        """Set up test method 'create_new_observation'"""

        self.admin = UserFactory.create()
        self.project = ProjectFactory.create(creator=self.admin)

        self.socialaccount = SocialAccount.objects.create(
            user=self.admin, provider='facebook', uid='1')
        self.category = CategoryFactory.create(
            name='Tweets',
            creator=self.admin,
            project=self.project
        )

        self.field_text = TextFieldFactory.create(
            name='tweet',
            category=self.category
        )

        self.si_pull = SocialInteractionPullFactory(
            socialaccount=self.socialaccount,
            project=self.project,
            text_to_pull='#Project2')

        self.geo_tweet = {
            'geometry':
                {u'type': u'Point', u'coordinates': [-0.1350858, 51.5246635]},
            'text': u'#Project2 scorpion @adeuonce',
            'created_at': datetime.datetime(2017, 5, 23, 14, 43, 1),
            'id': 867028097530572801,
            'user': u'Pepito Grillo'}

    def test_method_create_new_observation(self):

        init_obs = Observation.objects.all()

        create_new_observation(
            self.si_pull,
            self.geo_tweet,
            self.category,
            self.field_text
        )

        self.assertNotEqual(init_obs, Observation.objects.all())

