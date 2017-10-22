from django.test import TestCase

from allauth.socialaccount.models import SocialAccount

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from ..models import SocialInteraction


class CreateSocialInteractionTest(TestCase):

    def test_create_social_interaction(self):
        """ test create method for social interagration model. """
        creator = UserFactory.create()
        project = ProjectFactory.create(creator=creator)
        socialaccount_1 = SocialAccount.objects.create(
            user=creator, provider='facebook', uid='1')
        socialaccount_2 = SocialAccount.objects.create(
            user=creator, provider='facebook', uid='2')
        socialaccount_3 = SocialAccount.objects.create(
            user=creator, provider='google', uid='3')

        socialaccounts_list = [socialaccount_1, socialaccount_2]
        socialinteraction = SocialInteraction.create(
            'Test', 'Test desc', project, socialaccounts_list, creator
        )
        socialaccounts_all = socialinteraction.socialaccounts.all()
        self.assertIn(socialaccount_1, socialaccounts_all)
        self.assertIn(socialaccount_2, socialaccounts_all)
        self.assertNotIn(socialaccount_3, socialaccounts_all)


class UpdateSocialinteractionTest(TestCase):

    def test_update_seocial_interaction(self):
        """ test update method for social interagration model. """
        creator = UserFactory.create()
        project = ProjectFactory.create(creator=creator)
        socialaccount_1 = SocialAccount.objects.create(
            user=creator, provider='facebook', uid='1')
        socialaccount_2 = SocialAccount.objects.create(
            user=creator, provider='facebook', uid='2')

        socialaccounts = [socialaccount_1, socialaccount_2]
        socialinteraction = SocialInteraction.create(
            'Test', 'Test desc', project, socialaccounts, creator
        )

        new_name = "New name"
        new_description = "New Description"
        new_socialaccounts = [socialaccount_1]
        socialinteraction.update(
            socialinteraction.id,
            new_name,
            new_description,
            new_socialaccounts
        )

        socialaccounts_check = socialinteraction.socialaccounts.all()
        self.assertIn(socialaccount_1, socialaccounts_check)
        self.assertNotIn(socialaccount_2, socialaccounts_check)
