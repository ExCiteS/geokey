"""Tests for logger: model Project."""

from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory


class LogProjectTest(TestCase):
    """Test model Project."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})

    def test_log_create(self):
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, project_id)
        self.assertEqual(history.name, project_name)

    def test_log_update_name(self):
        """Test when name changes."""
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.project.name})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.name, original_name)

    def test_log_update_status(self):
        """Test when status changes."""
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.project.status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.status, original_status)

    def test_log_update_isprivate(self):
        """Test when privacy changes."""
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'isprivate',
            'value': str(self.project.isprivate)})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.isprivate, original_isprivate)

    def test_log_update_islocked(self):
        """Test when locker changes."""
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'islocked',
            'value': str(self.project.islocked)})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.islocked, original_islocked)

    def test_log_update_contributing_permissions(self):
        """Test when contributing permissions changes."""
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
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

    def test_log_update_geographic_extent(self):
        """Test when geographic extent changes."""
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
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'geographic_extent',
            'value': self.project.geographic_extent.json})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.geographic_extent, original_geographic_extent)

    def test_log_update_multiple_fields(self):
        """Test when multiple model fields changes."""
        log_count_init = LoggerHistory.objects.count()
        original_isprivate = self.project.isprivate
        original_islocked = self.project.islocked
        self.project.isprivate = False
        self.project.islocked = True
        self.project.save()

        log_count = LoggerHistory.objects.count()
        self.assertEqual(log_count, log_count_init + 2)

        logs = LoggerHistory.objects.all().order_by('-pk')[:2]

        # 1st changed field
        self.assertNotEqual(logs[0].user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(logs[0].project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(logs[0].category, None)
        self.assertEqual(logs[0].field, None)
        self.assertEqual(logs[0].action, {
            'id': 'updated',
            'field': 'islocked',
            'value': str(self.project.islocked)})
        history_1 = self.project.history.get(pk=logs[0].historical.get('id'))
        self.assertEqual(history_1.id, self.project.id)
        self.assertEqual(history_1.isprivate, original_isprivate)
        self.assertEqual(history_1.islocked, original_islocked)

        # 2st changed field
        self.assertNotEqual(logs[1].user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(logs[1].project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(logs[1].category, None)
        self.assertEqual(logs[1].field, None)
        self.assertEqual(logs[1].action, {
            'id': 'updated',
            'field': 'isprivate',
            'value': str(self.project.isprivate)})
        history_2 = self.project.history.get(pk=logs[1].historical.get('id'))
        self.assertEqual(history_2.id, self.project.id)
        self.assertEqual(history_2.isprivate, original_isprivate)
        self.assertEqual(history_2.islocked, original_islocked)

        # History entry is only one per save
        self.assertEqual(history_1, history_2)
