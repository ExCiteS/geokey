import datetime
import factory

from users.tests.model_factories import UserF

from ..models import Project


class ProjectF(factory.django.DjangoModelFactory):
    FACTORY_FOR = Project

    name = factory.Sequence(lambda n: 'project %d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    isprivate = True
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserF)
    status = 'active'

    @factory.post_generation
    def add_admins(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.admins.add(user)

    @factory.post_generation
    def add_contributors(self, create, extracted, **kwargs):
        from users.tests.model_factories import UserGroupF
        if not create:
            return

        if extracted:
            UserGroupF(add_users=extracted, **{
                'project': self,
                'can_contribute': True
            })

    @factory.post_generation
    def add_viewers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            from dataviews.tests.model_factories import ViewFactory

            ViewFactory(add_viewers=extracted, **{
                'project': self
            })
