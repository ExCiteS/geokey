from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import ProjectF, UserF

from ..models import Location, Observation, Comment
from .model_factories import (
    LocationFactory, ObservationFactory, CommentFactory
)


class LocationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()

        self.project1 = ProjectF(add_admins=[self.admin])
        self.project2 = ProjectF(add_admins=[self.admin])
        self.public_location = LocationFactory(**{
            'private': False
        })
        self.private_location = LocationFactory(**{
            'private': True
        })
        self.private_for_project_location = LocationFactory(**{
            'private': True,
            'private_for_project': self.project1
        })

    def test_get_locations_for_project1_with_admin(self):
        locations = Location.objects.get_list(self.admin, self.project1.id)
        self.assertEqual(len(locations), 2)

    def test_get_locations_for_project2_with_admin(self):
        locations = Location.objects.get_list(self.admin, self.project2.id)
        self.assertEqual(len(locations), 1)

    def test_get_public_location_for_project1_with_admin(self):
        location = Location.objects.get_single(
            self.admin, self.project1.id, self.public_location.id)
        self.assertEqual(location, self.public_location)

    def test_get_project_location_for_project1_with_admin(self):
        location = Location.objects.get_single(
            self.admin, self.project1.id, self.private_for_project_location.id)
        self.assertEqual(location, self.private_for_project_location)

    @raises(PermissionDenied)
    def test_get_private_location_for_project1_with_admin(self):
        Location.objects.get_single(
            self.admin, self.project1.id, self.private_location.id)

    def test_get_public_location_for_project2_with_admin(self):
        location = Location.objects.get_single(
            self.admin, self.project2.id, self.public_location.id)
        self.assertEqual(location, self.public_location)

    @raises(PermissionDenied)
    def test_get_project_location_for_project2_with_admin(self):
        Location.objects.get_single(
            self.admin, self.project2.id, self.private_for_project_location.id)

    @raises(PermissionDenied)
    def test_get_private_location_for_project2_with_admin(self):
        Location.objects.get_single(
            self.admin, self.project2.id, self.private_location.id)


class ObservationTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def test_get_as_editor_with_creator(self):
        observation = Observation.objects.as_editor(
            self.creator, self.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    def test_get_as_editor_with_admin(self):
        observation = Observation.objects.as_editor(
            self.admin, self.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_as_editor_some_dude(self):
        some_dude = UserF.create()
        Observation.objects.as_editor(
            some_dude, self.project.id, self.observation.id)


class CommentTest(TestCase):
    def test_get_comments(self):
        observation = ObservationFactory.create()
        CommentFactory.create_batch(5, **{'commentto': observation})
        CommentFactory.create(**{
            'commentto': observation,
            'status': 'deleted'
        })
        comments = Comment.objects.all()
        self.assertEqual(len(comments), 5)
        for comment in comments:
            self.assertNotEqual(comment.status, 'deleted')
