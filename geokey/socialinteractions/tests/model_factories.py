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
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)

    @factory.post_generation
    def add_social_accounts(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for socialaccount in extracted:
                SocialAccounts.objects.create(
                    socialinteraction=self,
                    socialaccount=socialaccount
                )


class SocialAccountsFactory(factory.django.DjangoModelFactory):
    """Factory for a single social social account."""
    socialinteraction = factory.SubFactory(SocialInteractionFactory)
    socialaccount = SocialAccount()
