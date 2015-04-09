from django.test import TestCase

from geokey.projects.tests.model_factories import ProjectF
from geokey.users.tests.model_factories import UserF
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory
)
from .model_factories import GroupingFactory, RuleFactory

from ..serializers import GroupingSerializer


class DataGroupingSerializerTest(TestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF.create(add_admins=[admin])
        category_1 = CategoryFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'text',
            'category': category_1
        })
        category_2 = CategoryFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'bla',
            'category': category_2
        })

        ObservationFactory.create_batch(5, **{
            'project': project,
            'category': category_1,
            'properties': {'text': 'yes'}}
        )

        viewer = UserF.create()
        view = GroupingFactory(add_viewers=[viewer], **{'project': project})
        RuleFactory(**{
            'grouping': view,
            'category': category_1,
            'constraints': {'text': 'yes'}
        })

        serializer = GroupingSerializer(view, context={'user': admin})
        self.assertEqual(len(serializer.get_data(view).get('features')), 5)
        self.assertEqual(serializer.get_num_contributions(view), 5)
