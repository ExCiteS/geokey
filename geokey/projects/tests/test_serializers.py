"""Tests for serializers of projects."""

from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from geokey.users.tests.model_factories import UserFactory
from geokey.contributions.tests.model_factories import ObservationFactory

from .model_factories import ProjectFactory
from ..serializers import ProjectSerializer


class SerializerTest(TestCase):
    def test_get_subsets(self):
        project = ProjectFactory.create()
        serializer = ProjectSerializer(project)
        self.assertIsNotNone(serializer.get_subsets(project))

    def test_get_geographic_extent(self):
        project = ProjectFactory.create(**{'geographic_extent': None})
        serializer = ProjectSerializer(project)
        self.assertIsNone(serializer.get_geographic_extent(project))

        project = ProjectFactory.create()
        serializer = ProjectSerializer(project)
        self.assertIsNotNone(serializer.get_geographic_extent(project))

    def test_get_user_contributions(self):
        user = UserFactory.create()
        project = ProjectFactory.create()
        ObservationFactory.create_batch(
            5,
            **{'creator': user, 'project': project}
        )
        serializer = ProjectSerializer(project, context={'user': user})
        self.assertEqual(5, serializer.get_user_contributions(project))

        serializer = ProjectSerializer(
            project, context={'user': AnonymousUser()}
        )
        self.assertEqual(0, serializer.get_user_contributions(project))
