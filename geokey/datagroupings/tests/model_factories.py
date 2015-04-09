import datetime
import factory

from geokey.users.tests.model_factories import UserF
from geokey.projects.tests.model_factories import ProjectF
from geokey.categories.tests.model_factories import CategoryFactory

from ..models import Grouping, Rule


class GroupingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Grouping

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
            from geokey.users.tests.model_factories import (
                UserGroupF, GroupingUserGroupFactory
            )
            group = UserGroupF(add_users=extracted, **{
                'project': self.project,
                'can_contribute': False
            })

            GroupingUserGroupFactory(**{
                'grouping': self,
                'usergroup': group
            })


class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rule

    category = factory.SubFactory(CategoryFactory)
    grouping = factory.SubFactory(GroupingFactory)
    constraints = None
    status = 'active'
