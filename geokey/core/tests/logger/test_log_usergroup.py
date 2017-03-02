"""Tests for logger: model UserGroup."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.users.tests.model_factories import UserGroupFactory


class LogUserGroupTest(TestCase):
    """Test model UserGroup."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.usergroup = UserGroupFactory.create(**{
            'project': self.project})

    def test_log_create(self):
        """Test when user group gets created."""
        log_count_init = LoggerHistory.objects.count()
        usergroup = UserGroupFactory.create(**{
            'project': self.project})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, {
            'id': str(usergroup.id),
            'name': usergroup.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'UserGroup'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
        """Test when user group gets deleted."""
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
        self.assertEqual(log.usergroup, {
            'id': str(usergroup_id),
            'name': usergroup_name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'class': 'UserGroup'})
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
        self.assertEqual(log.usergroup, {
            'id': str(self.usergroup.id),
            'name': self.usergroup.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup',
            'field': 'name'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.name, original_name)

    def test_log_update_can_contribute_user_group(self):
        """Test when can contribute changes."""
        log_count_init = LoggerHistory.objects.count()
        original_can_contribute = self.usergroup.can_contribute
        self.usergroup.can_contribute = False
        self.usergroup.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, {
            'id': str(self.usergroup.id),
            'name': self.usergroup.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'can_contribute',
            'value': 'False'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_contribute, original_can_contribute)

        original_can_contribute = self.usergroup.can_contribute
        self.usergroup.can_contribute = True
        self.usergroup.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, {
            'id': str(self.usergroup.id),
            'name': self.usergroup.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'can_contribute',
            'value': 'True'})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_contribute, original_can_contribute)

    def test_log_update_can_moderate_user_group(self):
        """Test when can moderate changes."""
        log_count_init = LoggerHistory.objects.count()
        original_can_moderate = self.usergroup.can_moderate
        self.usergroup.can_moderate = True
        self.usergroup.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, {
            'id': str(self.usergroup.id),
            'name': self.usergroup.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'can_moderate',
            'value': 'True'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_moderate, original_can_moderate)

        original_can_moderate = self.usergroup.can_moderate
        self.usergroup.can_moderate = False
        self.usergroup.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, {
            'id': str(self.usergroup.id),
            'name': self.usergroup.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'can_moderate',
            'value': 'False'})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_moderate, original_can_moderate)
