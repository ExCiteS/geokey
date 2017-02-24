"""Tests for core models."""

from django.test import TestCase

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

    # USERS
    def test_log_create_user(self):
        """Test when user gets created."""
        log_count_init = LoggerHistory.objects.count()
        user = UserFactory.create()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(log.user_id, user.id)
        self.assertEqual(log.action_id, 'created')
        self.assertEqual(log.action, 'User created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_deleted_user(self):
        """Test when user gets deleted."""
        user = UserFactory.create()
        user_id = user.id
        log_count_init = LoggerHistory.objects.count()
        user.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(log.user_id, user_id)
        self.assertEqual(log.action_id, 'deleted')
        self.assertEqual(log.action, 'User deleted')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_user(self):
        """Test when user changes name."""
        user = UserFactory.create()
        log_count_init = LoggerHistory.objects.count()
        user.display_name = '%s UPDATED' % user.display_name
        user.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(log.user_id, user.id)
        self.assertEqual(log.action_id, 'updated')
        self.assertEqual(log.action, 'User renamed')
        self.assertEqual(log_count, log_count_init + 1)
