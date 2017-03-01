"""Tests for logger: model Subset."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.subsets.tests.model_factories import SubsetFactory


class LogSubsetTest(TestCase):
    """Test model Subset."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.subset = SubsetFactory.create(**{
            'creator': self.user,
            'project': self.project})

    def test_log_create(self):
        """Test when subset gets created."""
        log_count_init = LoggerHistory.objects.count()
        subset = SubsetFactory.create(**{
            'creator': self.user,
            'project': self.project})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, {
            'id': str(subset.id),
            'name': subset.name})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_name(self):
        """Test when name changes."""
        log_count_init = LoggerHistory.objects.count()
        original_name = self.subset.name
        self.subset.name = '%s UPDATED' % self.subset.name
        self.subset.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, {
            'id': str(self.subset.id),
            'name': self.subset.name})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.subset.name})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.subset.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.subset.id)
        self.assertEqual(history.name, original_name)
