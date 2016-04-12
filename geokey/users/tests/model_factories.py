"""Model factories used for tests of users."""

import datetime
import factory
import string

from factory.fuzzy import FuzzyText

from django.utils import timezone

from oauth2_provider.models import AccessToken

from ..models import User, UserGroup


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    display_name = factory.Sequence(lambda n: "display_name%s" % n)
    email = factory.Sequence(lambda n: "email%s@example.com" % n)
    password = ''
    is_active = True
    is_superuser = False

    last_login = timezone.datetime(2000, 1, 1).replace(tzinfo=timezone.utc)
    date_joined = timezone.datetime(1999, 1, 1).replace(
        tzinfo=timezone.utc)

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


# don't move this import to the top of the file! (it would cause an import cycle):
from geokey.applications.tests.model_factories import ApplicationFactory

class AccessTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccessToken
        django_get_or_create = ('user', 'application')

    user = factory.SubFactory(UserFactory)
    application = factory.SubFactory(ApplicationFactory)
    token = FuzzyText(length=30, chars=string.ascii_uppercase + string.digits)
    expires = timezone.now() + datetime.timedelta(days=1)
    scope = 'read write'


class UserGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserGroup

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    project = factory.SubFactory(
        'geokey.projects.tests.model_factories.ProjectFactory')
    can_contribute = True
    can_moderate = False

    @factory.post_generation
    def add_users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)
