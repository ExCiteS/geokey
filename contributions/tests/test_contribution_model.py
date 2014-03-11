from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import ProjectF, UserGroupF, UserF

from ..models import Location, Observation, Comment

from .model_factories import (
    LocationFactory, ObservationFactory, CommentFactory
)


class LocationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()

        self.project1 = ProjectF(**{
            'admins': UserGroupF(add_users=[self.admin]),
        })
        self.project2 = ProjectF(**{
            'admins': UserGroupF(add_users=[self.admin]),
        })
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

    # ########################################################################
    #
    # LOCATIONS
    #
    # ########################################################################

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

    # ########################################################################
    #
    # OBSERVATIONS
    #
    # ########################################################################

    @raises(Observation.DoesNotExist)
    def test_delete_observation(self):
        observation = ObservationFactory()
        observation.delete()
        Observation.objects.get(pk=observation.id)

    # ########################################################################
    #
    # COMMENTS
    #
    # ########################################################################

    @raises(Comment.DoesNotExist)
    def test_delete_comment(self):
        comment = CommentFactory()
        comment.delete()
        Comment.objects.get(pk=comment.id)
