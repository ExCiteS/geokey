import datetime
import factory

from projects.tests.model_factories import UserF, ProjectF
from observationtypes.tests.model_factories import ObservationTypeFactory

from ..models import Location, Observation, Comment


class LocationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Location

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    geometry = 'POINT(-0.1340407133102417 51.52447878755655)'
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserF)
    status = 'active'
    version = 1
    private = False
    private_for_project = None


class ObservationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Observation

    location = factory.SubFactory(LocationFactory)
    project = factory.SubFactory(ProjectF)
    status = 'active'
    observationtype = factory.SubFactory(ObservationTypeFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Comment

    text = factory.Sequence(lambda n: 'Comment number %d' % n)
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserF)
    commentto = factory.SubFactory(ObservationFactory)
    respondsto = None
    status = 'active'
