"""Tests for core models."""

from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory

from ..models import LoggerHistory


class LoggerHistoryTest(TestCase):
    """Test LoggerHistory."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})

    # USERS
    def test_log_create_user(self):
        """Test when user gets created."""
        log_count_init = LoggerHistory.objects.count()
        UserFactory.create()
        self.assertEqual(LoggerHistory.objects.count(), log_count_init)

    def test_log_delete_user(self):
        """Test when user gets deleted."""
        log_count_init = LoggerHistory.objects.count()
        self.user.delete()
        self.assertEqual(LoggerHistory.objects.count(), log_count_init)

    def test_log_update_user_display_name(self):
        """Test when user changes display name."""
        log_count_init = LoggerHistory.objects.count()
        self.user.display_name = '%s UPDATED' % self.user.display_name
        self.user.save()
        self.assertEqual(LoggerHistory.objects.count(), log_count_init)

    # PROJECTS
    def test_log_create_project(self):
        """Test when project gets created."""
        log_count_init = LoggerHistory.objects.count()
        project = ProjectFactory.create(**{'creator': self.user})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(project.id),
            'name': project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log.historical, None)
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_delete_project(self):
        """Test when project gets deleted."""
        project_id = self.project.id
        project_name = self.project.name
        log_count_init = LoggerHistory.objects.count()
        self.project.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(project_id),
            'name': project_name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, project_id)
        self.assertEqual(history.name, project_name)

    def test_log_update_project_name(self):
        """Test when project name changes."""
        log_count_init = LoggerHistory.objects.count()
        original_name = self.project.name
        self.project.name = '%s UPDATED' % self.project.name
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.project.name})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.name, original_name)

    def test_log_update_project_status(self):
        """Test when project status changes."""
        log_count_init = LoggerHistory.objects.count()

        original_status = self.project.status
        self.project.status = 'inactive'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.project.status})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.status, original_status)

        original_status = self.project.status
        self.project.status = 'active'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.project.status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.status, original_status)

    def test_log_update_project_isprivate(self):
        """Test when project privacy changes."""
        log_count_init = LoggerHistory.objects.count()

        original_isprivate = self.project.isprivate
        self.project.isprivate = False
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'isprivate',
            'value': str(self.project.isprivate)})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.isprivate, original_isprivate)

        original_isprivate = self.project.isprivate
        self.project.isprivate = True
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'isprivate',
            'value': str(self.project.isprivate)})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.isprivate, original_isprivate)

    def test_log_update_project_islocked(self):
        """Test when project locker changes."""
        log_count_init = LoggerHistory.objects.count()

        original_islocked = self.project.islocked
        self.project.islocked = True
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'islocked',
            'value': str(self.project.islocked)})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.islocked, original_islocked)

        original_islocked = self.project.islocked
        self.project.islocked = False
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'islocked',
            'value': str(self.project.islocked)})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.islocked, original_islocked)


    def test_log_update_project_contributing_permissions(self):
        """Test when project contributing permissions changes."""
        log_count_init = LoggerHistory.objects.count()

        original_everyone_contributes = self.project.everyone_contributes
        self.project.everyone_contributes = 'auth'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'everyone_contributes',
            'value': self.project.everyone_contributes})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(
            history.everyone_contributes,
            original_everyone_contributes)

        original_everyone_contributes = self.project.everyone_contributes
        self.project.everyone_contributes = 'false'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'everyone_contributes',
            'value': self.project.everyone_contributes})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(
            history.everyone_contributes,
            original_everyone_contributes)

        original_everyone_contributes = self.project.everyone_contributes
        self.project.everyone_contributes = 'true'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'everyone_contributes',
            'value': self.project.everyone_contributes})
        self.assertEqual(log_count, log_count_init + 3)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(
            history.everyone_contributes,
            original_everyone_contributes)

    def test_log_update_project_geo_extent(self):
        """Test when project geo. extent changes."""
        log_count_init = LoggerHistory.objects.count()
        original_geographic_extent = self.project.geographic_extent
        self.project.geographic_extent = GEOSGeometry(
            '{"type": "Polygon","coordinates":'
            '[[[-0.505,51.682],[-0.53,51.327],'
            '[0.225,51.323],[0.167,51.667],[-0.505,51.682]]]}')
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'geographic_extent',
            'value': self.project.geographic_extent.json})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.geographic_extent, original_geographic_extent)

    # CATEGORIES
    def test_log_create_category(self):
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
        self.assertEqual(log.category, {
            'id': str(category.id),
            'name': category.name})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete_category(self):
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
        self.assertEqual(log.category, {
            'id': str(category_id),
            'name': category_name})
        self.assertEqual(log.action, {
            'id': 'deleted',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, category_id)
        self.assertEqual(history.name, category_name)

    def test_log_update_category_name(self):
        """Test when category name changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.category.name})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.name, original_name)

    def test_log_update_category_status(self):
        """Test when category status changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.action, {
            'id': 'updated',
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.category.status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.status, original_status)

    def test_log_update_category_default_status(self):
        """Test when category default status changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.action, {
            'id': 'updated',
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'default_status',
            'value': self.category.default_status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.default_status, original_default_status)
