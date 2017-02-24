"""Tests for core models."""

from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from geokey.users.tests.model_factories import UserFactory, UserGroupFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.contributions.tests.model_factories import (
    LocationFactory,
    ObservationFactory,
    CommentFactory,
)
from geokey.subsets.tests.model_factories import SubsetFactory

from ..models import LoggerHistory


class LoggerHistoryTest(TestCase):
    """Test LoggerHistory."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{'creator': self.user})

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

        self.assertNotEqual(log.user_id, self.user.id)
        self.assertEqual(log.project_id, project.id)
        self.assertEqual(log.action_id, 'created')
        self.assertEqual(log.action, 'Project created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_delete_project(self):
        """Test when project gets deleted."""
        project_id = self.project.id
        log_count_init = LoggerHistory.objects.count()
        self.project.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user_id, self.user.id)
        self.assertEqual(log.project_id, project_id)
        self.assertEqual(log.action_id, 'deleted')
        self.assertEqual(log.action, 'Project deleted')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_project_name(self):
        """Test when project name changes."""
        log_count_init = LoggerHistory.objects.count()
        self.project.name = '%s UPDATED' % self.project.name
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user_id, self.user.id)
        self.assertEqual(log.project_id, self.project.id)
        self.assertEqual(log.action_id, 'updated')
        self.assertEqual(log.action, 'Project renamed')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_project_status(self):
        """Test when project status changes."""
        log_count_init = LoggerHistory.objects.count()
        self.project.status = 'inactive'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user_id, self.user.id)
        self.assertEqual(log.project_id, self.project.id)
        self.assertEqual(log.action_id, 'updated')
        self.assertEqual(log.action, 'Project is archived')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_project_isprivate(self):
        """Test when project privacy changes."""
        log_count_init = LoggerHistory.objects.count()
        self.project.isprivate = False
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user_id, self.user.id)
        self.assertEqual(log.project_id, self.project.id)
        self.assertEqual(log.action_id, 'updated')
        self.assertEqual(log.action, 'Project is public')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_project_contributing_permissions(self):
        """Test when project contributing permissions changes."""
        log_count_init = LoggerHistory.objects.count()
        self.project.everyone_contributes = 'auth'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user_id, self.user.id)
        self.assertEqual(log.project_id, self.project.id)
        self.assertEqual(log.action_id, 'updated')
        self.assertEqual(log.action, 'Project permissions changed')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_project_islocked(self):
        """Test when project locker changes."""
        log_count_init = LoggerHistory.objects.count()
        self.project.islocked = True
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user_id, self.user.id)
        self.assertEqual(log.project_id, self.project.id)
        self.assertEqual(log.action_id, 'updated')
        self.assertEqual(log.action, 'Project is locked')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_project_geo_extent(self):
        """Test when project geo. extent changes."""
        log_count_init = LoggerHistory.objects.count()
        self.project.geographic_extent = GEOSGeometry(
            '{"type": "Polygon","coordinates": [[[55.32,50.25],[-0.58,58.36],'
            '[55.22,59.32],[0.18,59.02],[-0.99,54.68]]]}')
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user_id, self.user.id)
        self.assertEqual(log.project_id, self.project.id)
        self.assertEqual(log.action_id, 'updated')
        self.assertEqual(log.action, 'Project geogr. ext. changed')
        self.assertEqual(log_count, log_count_init + 1)
