"""Tests for logger: model Subset."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.users.tests.model_factories import UserGroupFactory


class LogSubsetTest(TestCase):
    """Test model Subset."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.usergroup = UserGroupFactory.create(**{'project': self.project})

    def test_log_create(self):
        """Test when subset gets created."""
        log_count_init = LoggerHistory.objects.count()
        usergroup = UserGroupFactory.create(**{'project': self.project})

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
        self.assertEqual(log.usergroup, {
            'id': str(usergroup.id),
            'name': usergroup.name})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
        """Test when subset gets deleted."""
        usergroup_id = self.usergroup.id
        usergroup_name = self.usergroup.name
        log_count_init = LoggerHistory.objects.count()
        self.usergroup.delete()

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
        self.assertEqual(log.usergroup, {
            'id': str(usergroup_id),
            'name': usergroup_name})
        self.assertEqual(log.action, {
            'id': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_name(self):
        """Test when name changes."""
        log_count_init = LoggerHistory.objects.count()
        original_name = self.usergroup.name
        self.usergroup.name = '%s UPDATED' % self.usergroup.name
        self.usergroup.save()

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
        self.assertEqual(log.usergroup, {
            'id': str(self.usergroup.id),
            'name': self.usergroup.name})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.usergroup.name})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.name, original_name)
