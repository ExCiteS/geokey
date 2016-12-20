"""Model factories used for tests of social interactions."""

import factory

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from allauth.socialaccount.models import SocialAccount

from ..models import SocialInteraction, SocialAccounts


class SocialInteractionFactory(factory.django.DjangoModelFactory):
    """Factory for a single social interaction."""
    class Meta:
        """Factory meta information."""
        model = SocialInteraction

    name = factory.Sequence(lambda n: 'social interaction %d' % n)
    description = factory.Sequence(lambda n: '%d description' % n)
    creator = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    text_to_post = factory.Sequence(lambda n: 'text to post %d' % n)

    @factory.post_generation
    def add_social_accounts(obj, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for socialaccount in extracted:
                SocialAccounts.objects.create(
                    socialinteraction=obj,
                    socialaccount=socialaccount
                )
                obj.socialaccounts.add(socialaccount)
                obj.save()


class SocialAccountsFactory(factory.django.DjangoModelFactory):
    """Factory for a single social social account."""
    socialinteraction = factory.SubFactory(SocialInteractionFactory)
    socialaccount = SocialAccount()
