"""Model factories used for tests of applications."""

import datetime
import factory

from geokey.users.tests.model_factories import UserFactory

from ..models import Application


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    created_at = datetime.date(2014, 11, 11)
    user = factory.SubFactory(UserFactory)
    download_url = 'http://example.com'
    redirect_uris = ['http://example.com/app']
    status = 'active'
