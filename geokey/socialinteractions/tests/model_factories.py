"""Model factories used for tests of socialinteractions."""

import factory

from allauth.socialaccount.models import SocialAccount

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from ..models import SocialInteraction, SocialInteractionPull


class SocialInteractionFactoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialInteraction

    creator = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: 'category %s' % n)
    text_to_post = factory.LazyAttribute(lambda o: '%s Text_text' % o.name)
    project = factory.SubFactory(ProjectFactory)
    status = 'active'
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    socialaccount = SocialAccount()


class SocialInteractionPullFactoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialInteractionPull

    creator = factory.SubFactory(UserFactory)
    text_to_post = factory.LazyAttribute(lambda o: '%s Text_text' % o.name)
    project = factory.SubFactory(ProjectFactory)
    status = 'active'
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    socialaccount = SocialAccount()
    frequency = '5min'
    socialaccount = SocialAccount()
