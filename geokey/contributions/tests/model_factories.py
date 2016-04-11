"""Model factories used for tests of contributions."""

import datetime
import factory

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory

from ..models import Location, Observation, Comment


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    geometry = 'POINT(-0.134040713310241 51.52447878755655)'
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserFactory)
    status = 'active'
    version = 1
    private = False
    private_for_project = None


class ObservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Observation

    location = factory.SubFactory(LocationFactory)
    project = factory.SubFactory(ProjectFactory)
    status = 'active'
    category = factory.SubFactory(CategoryFactory)
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserFactory)
    version = 1


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    text = factory.Sequence(lambda n: 'Comment number %d' % n)
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserFactory)
    commentto = factory.SubFactory(ObservationFactory)
    respondsto = None
    status = 'active'
