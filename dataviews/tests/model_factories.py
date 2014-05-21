import datetime
import factory

from users.tests.model_factories import UserF
from projects.tests.model_factories import ProjectF
from observationtypes.tests.model_factories import ObservationTypeFactory

from ..models import View, Rule


class ViewFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = View

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserF)
    created_at = datetime.date(2014, 11, 11)
    status = 'active'
    isprivate = True
    project = factory.SubFactory(ProjectF)

    @factory.post_generation
    def add_viewers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            from users.tests.model_factories import (
                UserGroupF, ViewUserGroupFactory
            )
            group = UserGroupF(add_users=extracted, **{
                'project': self.project,
                'can_contribute': False
            })

            ViewUserGroupFactory(**{
                'view': self,
                'usergroup': group
            })


class RuleFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Rule

    observation_type = factory.SubFactory(ObservationTypeFactory)
    view = factory.SubFactory(ViewFactory)
    filters = None
    status = 'active'
