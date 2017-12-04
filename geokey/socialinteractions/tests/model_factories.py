"""Model factories used for tests of socialinteractions."""

import factory

from allauth.socialaccount.models import SocialAccount

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from ..models import SocialInteractionPost, SocialInteractionPull


class SocialInteractionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialInteractionPost

    creator = factory.SubFactory(UserFactory)
    text_to_post = 'Text to post including $link$'
    link = 'www.link.com'
    project = factory.SubFactory(ProjectFactory)
    status = 'active'
    socialaccount = SocialAccount()


class SocialInteractionPullFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialInteractionPull

    creator = factory.SubFactory(UserFactory)
    text_to_pull = '#Project2'
    project = factory.SubFactory(ProjectFactory)
    status = 'active'
    socialaccount = SocialAccount()
    frequency = '5min'
