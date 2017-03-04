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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup',
            'field': 'name'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.name, original_name)

    def test_log_update_can_contribute(self):
        """Test when setting gets set to `can contribute`."""
        self.usergroup.can_contribute = False
        self.usergroup.can_moderate = False
        self.usergroup.save()
        log_count_init = LoggerHistory.objects.count()
        original_can_contribute = self.usergroup.can_contribute
        original_can_moderate = self.usergroup.can_moderate
        self.usergroup.can_contribute = True
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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup',
            'field': 'can_contribute',
            'value': 'True'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_contribute, original_can_contribute)
        self.assertEqual(history.can_moderate, original_can_moderate)

        self.usergroup.can_contribute = False
        self.usergroup.can_moderate = True
        self.usergroup.save()
        log_count_init = LoggerHistory.objects.count()
        original_can_contribute = self.usergroup.can_contribute
        original_can_moderate = self.usergroup.can_moderate
        self.usergroup.can_contribute = True
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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup',
            'field': 'can_contribute',
            'value': 'True'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_contribute, original_can_contribute)
        self.assertEqual(history.can_moderate, original_can_moderate)

    def test_log_update_can_moderate(self):
        """Test when setting gets set to `can moderate`."""
        self.usergroup.can_contribute = False
        self.usergroup.can_moderate = False
        self.usergroup.save()
        log_count_init = LoggerHistory.objects.count()
        original_can_contribute = self.usergroup.can_contribute
        original_can_moderate = self.usergroup.can_moderate
        self.usergroup.can_contribute = True
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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup',
            'field': 'can_moderate',
            'value': 'True'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_contribute, original_can_contribute)
        self.assertEqual(history.can_moderate, original_can_moderate)

        self.usergroup.can_contribute = True
        self.usergroup.can_moderate = False
        self.usergroup.save()
        log_count_init = LoggerHistory.objects.count()
        original_can_contribute = self.usergroup.can_contribute
        original_can_moderate = self.usergroup.can_moderate
        self.usergroup.can_contribute = True
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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup',
            'field': 'can_moderate',
            'value': 'True'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_contribute, original_can_contribute)
        self.assertEqual(history.can_moderate, original_can_moderate)

    def test_log_update_can_view(self):
        """Test when setting gets set to `can view`."""
        self.usergroup.can_contribute = True
        self.usergroup.can_moderate = False
        self.usergroup.save()
        log_count_init = LoggerHistory.objects.count()
        original_can_contribute = self.usergroup.can_contribute
        original_can_moderate = self.usergroup.can_moderate
        self.usergroup.can_contribute = False
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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup',
            'field': 'can_view',
            'value': 'True'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_contribute, original_can_contribute)
        self.assertEqual(history.can_moderate, original_can_moderate)

        self.usergroup.can_contribute = True
        self.usergroup.can_moderate = True
        self.usergroup.save()
        log_count_init = LoggerHistory.objects.count()
        original_can_contribute = self.usergroup.can_contribute
        original_can_moderate = self.usergroup.can_moderate
        self.usergroup.can_contribute = False
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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup',
            'field': 'can_view',
            'value': 'True'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.usergroup.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.usergroup.id)
        self.assertEqual(history.can_contribute, original_can_contribute)
        self.assertEqual(history.can_moderate, original_can_moderate)

    def test_log_add_user(self):
        """Test when user is added."""
        log_count_init = LoggerHistory.objects.count()
        new_user = UserFactory.create()
        self.usergroup.users.add(new_user)

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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup_users',
            'subaction': 'add',
            'user_id': str(new_user.id),
            'user_display_name': new_user.display_name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_remove_user(self):
        """Test when user is removed."""
        existing_user = UserFactory.create()
        self.usergroup.users.add(existing_user)
        log_count_init = LoggerHistory.objects.count()
        self.usergroup.users.remove(existing_user)

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
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'UserGroup_users',
            'subaction': 'remove',
            'user_id': str(existing_user.id),
            'user_display_name': existing_user.display_name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)
