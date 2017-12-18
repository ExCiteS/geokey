"""Test for utils."""

from django.test import TestCase
from django.utils import timezone

from allauth.socialaccount.models import SocialAccount, SocialApp

from geokey.socialinteractions.utils import (
    start2pull,
    check_dates,
    create_new_observation,
    get_category_and_field,
    pull_from_social_media
)
from geokey.categories.tests.model_factories import CategoryFactory, TextFieldFactory, NumericFieldFactory

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.socialinteractions.tests.model_factories import SocialInteractionPullFactory
from geokey.socialinteractions.models import get_ready_to_post
from geokey.contributions.models import Observation
from geokey.contributions.tests.model_factories import ObservationFactory

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
            key='tweet',
            category=self.category
        )

        self.tweet_id_field = NumericFieldFactory.create(
            key='tweet-id',
            category=self.category
        )

    def test_method_when_check_when_category_and_field_exists(self):
        """Check method when category and field exists."""
        tweet_cat, text_field, tweet_id_field = get_category_and_field(
            self.project,
            self.socialaccount)

        self.assertEqual(tweet_cat.id, self.category.id)
        self.assertEqual(tweet_cat.name, self.category.name)

        self.assertEqual(text_field.id, self.field_text.id)
        self.assertEqual(text_field.key, self.field_text.key)

        self.assertEqual(tweet_id_field.id, self.tweet_id_field.id)
        self.assertEqual(tweet_id_field.key, self.tweet_id_field.key)

    def test_method_when_check_when_category_and_field_does_not_exist(self):
        """Check method when category does not exist and field exists."""
        self.category.delete()
        self.category.save()

        tweet_cat, text_field, tweet_id_field = get_category_and_field(
            self.project,
            self.socialaccount)

        self.assertNotEqual(tweet_cat.id, self.category.id)
        self.assertEqual(tweet_cat.name, self.category.name)

        self.assertNotEqual(text_field.id, self.field_text.id)
        self.assertEqual(text_field.key, self.field_text.key)

        self.assertNotEqual(tweet_id_field.id, self.tweet_id_field.id)
        self.assertEqual(tweet_id_field.key, self.tweet_id_field.key)


class CreateNewObservationTest(TestCase):
    """Test for method 'create_new_observation'."""

    def setUp(self):
        """Set up test method 'create_new_observation'."""
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
            key='tweet',
            category=self.category
        )

        self.tweet_id_field = NumericFieldFactory.create(
            key='tweet-id',
            category=self.category
        )

        self.si_pull = SocialInteractionPullFactory.create(
            socialaccount=self.socialaccount,
            project=self.project,
            creator=self.admin)

        self.geo_tweet = {
            'geometry': u'POINT (-0.1350858 51.5246635)',
            'text': u'#Project2 scorpion @adeuonce',
            'created_at': datetime(2017, 5, 23, 14, 43, 1),
            'id': 867028097530572801,
            'user': u'Pepito Grillo'}

    def test_method_create_new_observation(self):
        """Test for method 'create_new_observation'."""
        init_obs = Observation.objects.count()

        create_new_observation(
            self.si_pull,
            self.geo_tweet,
            self.category,
            self.field_text,
            self.tweet_id_field
        )

        self.assertEqual(init_obs + 1, Observation.objects.count())


class PullFromSocialMediaTest(TestCase):
    """Test for pull_from_social_media."""

    def setUp(self):
        """Setup for test."""
        self.provider = 'twitter'
        self.text_to_pull = '#Project2'
        self.since_id = 928637049644646400
        self.admin_user = UserFactory.create()
        self.app = SocialApp.objects.create(
            provider='twitter',
            name='Twitter',
            client_id='xxxxxxxxxxxxxxxxxx',
            secret='xxxxxxxxxxxxxxxxxx',
            key=''
        )
        self.socialaccount = SocialAccount.objects.create(
            user=self.admin_user, provider='twitter', uid='1')

    def test_pull_from_social_media_with_fake_app(self):
        """Test pull_from_social_media with fake app."""
        access_token = 'ahahashasgasgasfgas'
        value = pull_from_social_media(
            self.provider,
            access_token,
            self.text_to_pull,
            self.since_id,
            self.app)
        self.assertEqual(value, "You are not authenticated")


class GetReadyToPostTest(TestCase):
    """Test for get_ready_to_post."""

    def setUp(self):
        """Setup for test."""
        self.user = UserFactory.create()
        self.category_tweet = CategoryFactory.create(
            name="Tweets")

        self.observation = ObservationFactory.create()
        self.observation_tweet = ObservationFactory.create(
            category=self.category_tweet)

    def test_method_with_regular_category(self):
        """Test method with regular category."""
        value = get_ready_to_post(self.observation)

        self.assertEqual(value, "posted to social media")

    def test_method_with_category_name_tweet(self):
        """Test method with category name as 'Tweets'."""
        value = get_ready_to_post(self.observation_tweet)

        self.assertEqual(value, "Category name is Tweets")
