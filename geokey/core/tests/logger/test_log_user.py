"""Tests for logger: model User."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory


class LogUserTest(TestCase):
    """Test model User."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()

    def test_log_create(self):
        """Test when user gets created."""
        log_count_init = LoggerHistory.objects.count()
        UserFactory.create()
        self.assertEqual(LoggerHistory.objects.count(), log_count_init)

    def test_log_update_display_name(self):
        """Test when display name changes."""
        log_count_init = LoggerHistory.objects.count()
        self.user.display_name = '%s UPDATED' % self.user.display_name
        self.user.save()
        self.assertEqual(LoggerHistory.objects.count(), log_count_init)
