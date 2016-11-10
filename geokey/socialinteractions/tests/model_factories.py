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

    name = factory.Sequence(lambda n: 'project %d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    socialaccounts = SocialAccount()

class SocialAccountsFactory(factory.django.DjangoModelFactory):
    """Factory for a single social social account."""
    socialinteraction = factory.SubFactory(SocialInteractionFactory)
    socialaccount = SocialAccount()
