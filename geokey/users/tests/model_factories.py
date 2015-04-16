import factory

from django.utils import timezone

from ..models import User, UserGroup, GroupingUserGroup


class UserF(factory.django.DjangoModelFactory):
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
        user = super(UserF, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class UserGroupF(factory.django.DjangoModelFactory):
    class Meta:
        model = UserGroup

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    project = factory.SubFactory(
        'geokey.projects.tests.model_factories.ProjectF')
    can_contribute = True
    can_moderate = False

    @factory.post_generation
    def add_users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)


class GroupingUserGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GroupingUserGroup

    usergroup = factory.SubFactory(UserGroupF)
    grouping = factory.SubFactory(
        'datagroupings.tests.model_factories.GroupingFactory'
    )
    can_read = True
    can_view = True
