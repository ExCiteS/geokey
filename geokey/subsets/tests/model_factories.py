import factory

from geokey.users.tests.model_factories import UserF
from geokey.projects.tests.model_factories import ProjectF

from ..models import Subset


class SubsetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subset

    name = factory.Sequence(lambda n: 'project %d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserF)
    project = factory.SubFactory(ProjectF)
