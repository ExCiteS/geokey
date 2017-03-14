"""Tests for logger: model Location."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.contributions.tests.model_factories import LocationFactory


class LogLocationFieldTest(TestCase):
    """Test model Location."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.location = LocationFactory.create(**{
            'creator': self.user})

    def test_log_create(self):
        """Test when location gets created."""
        log_count_init = LoggerHistory.objects.count()
        location = LocationFactory.create(**{
            'creator': self.user})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, None)
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, {
            'id': str(location.id),
            'name': location.name})
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'Location'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
        """Test when location gets deleted."""
        location_id = self.location.id
        location_name = self.location.name
        log_count_init = LoggerHistory.objects.count()
        self.location.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, None)
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, {
            'id': str(location_id),
            'name': location_name})
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'class': 'Location'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_name(self):
        """Test when name changes."""
        log_count_init = LoggerHistory.objects.count()
        self.location.name = '%s UPDATED' % self.location.name
        self.location.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, None)
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Location',
            'field': 'name'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_geometry(self):
        """Test when geometry changes."""
        log_count_init = LoggerHistory.objects.count()
        self.location.geometry = 'POINT(-0.134140712210241 51.12547879755655)'
        self.location.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, None)
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Location',
            'field': 'geometry'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)
