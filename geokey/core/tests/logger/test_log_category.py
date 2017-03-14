"""Tests for logger: model Category."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory


class LogCategoryTest(TestCase):
    """Test model Category."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})

    def test_log_create(self):
        """Test when category gets created."""
        log_count_init = LoggerHistory.objects.count()
        category = CategoryFactory.create(**{
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
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(category.id),
            'name': category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'Category'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
        """Test when category gets deleted."""
        category_id = self.category.id
        category_name = self.category.name
        log_count_init = LoggerHistory.objects.count()
        self.category.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(category_id),
            'name': category_name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'class': 'Category',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, category_id)
        self.assertEqual(history.name, category_name)

    def test_log_update_name(self):
        """Test when name changes."""
        log_count_init = LoggerHistory.objects.count()
        original_name = self.category.name
        self.category.name = '%s UPDATED' % self.category.name
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Category',
            'field': 'name'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.name, original_name)

    def test_log_update_status(self):
        """Test when status changes."""
        log_count_init = LoggerHistory.objects.count()

        original_status = self.category.status
        self.category.status = 'inactive'
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Category',
            'field': 'status',
            'value': self.category.status})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.status, original_status)

        original_status = self.category.status
        self.category.status = 'active'
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Category',
            'field': 'status',
            'value': self.category.status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.status, original_status)

    def test_log_update_default_status(self):
        """Test when default status changes."""
        log_count_init = LoggerHistory.objects.count()

        original_default_status = self.category.default_status
        self.category.default_status = 'active'
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Category',
            'field': 'default_status',
            'value': self.category.default_status})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.default_status, original_default_status)

        original_default_status = self.category.default_status
        self.category.default_status = 'pending'
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Category',
            'field': 'default_status',
            'value': self.category.default_status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.default_status, original_default_status)

    def test_log_update_multiple_fields(self):
        """Test when multiple model fields changes."""
        log_count_init = LoggerHistory.objects.count()
        original_name = self.category.name
        original_status = self.category.status
        self.category.name = '%s UPDATED' % self.category.name
        self.category.status = 'inactive'
        self.category.save()

        log_count = LoggerHistory.objects.count()
        self.assertEqual(log_count, log_count_init + 2)

        logs = LoggerHistory.objects.all().order_by('-pk')[:2]

        # 1st changed field
        self.assertNotEqual(logs[1].user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(logs[1].project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(logs[1].category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(logs[1].field, None)
        self.assertEqual(logs[1].action, {
            'id': 'updated',
            'class': 'Category',
            'field': 'name'})
        history_2 = self.category.history.get(pk=logs[1].historical.get('id'))
        self.assertEqual(history_2.id, self.category.id)
        self.assertEqual(history_2.name, original_name)
        self.assertEqual(history_2.status, original_status)

        # 2nd changed field
        self.assertNotEqual(logs[0].user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(logs[0].project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(logs[0].category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(logs[0].field, None)
        self.assertEqual(logs[0].action, {
            'id': 'updated',
            'class': 'Category',
            'field': 'status',
            'value': self.category.status})
        history_1 = self.category.history.get(pk=logs[0].historical.get('id'))
        self.assertEqual(history_1.id, self.category.id)
        self.assertEqual(history_1.name, original_name)
        self.assertEqual(history_1.status, original_status)

        # History entry is only one per save
        self.assertEqual(history_1, history_2)
