"""Test Models for social interactions."""

import factory

from django.conf import settings
from django.db import models

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from allauth.socialaccount.models import SocialAccount

from ..models import SocialInteraction


class SocialInteractionFactory(factory.django.DjangoModelFactory):
    """Stores a single social interaction."""

    class Meta:
        model = SocialInteraction

    name = factory.Sequence(lambda n: 'project %d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    socialaccount = SocialAccount()
