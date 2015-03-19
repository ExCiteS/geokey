import datetime
import factory

from geokey.users.tests.model_factories import UserF
from geokey.projects.tests.model_factories import ProjectF
from geokey.categories.tests.model_factories import CategoryFactory

from ..models import Location, Observation, Comment


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    geometry = 'POINT(-0.134040713310241 51.52447878755655)'
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserF)
    status = 'active'
    version = 1
    private = False
    private_for_project = None


class ObservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Observation

    location = factory.SubFactory(LocationFactory)
    project = factory.SubFactory(ProjectF)
    status = 'active'
    category = factory.SubFactory(CategoryFactory)
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserF)
    version = 1


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    text = factory.Sequence(lambda n: 'Comment number %d' % n)
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserF)
    commentto = factory.SubFactory(ObservationFactory)
    respondsto = None
    status = 'active'
