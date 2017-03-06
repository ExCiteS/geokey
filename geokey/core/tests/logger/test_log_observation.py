"""Tests for logger: model Observation."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.contributions.tests.model_factories import (
    LocationFactory,
    ObservationFactory,
)


class LogObservationTest(TestCase):
    """Test model Observation."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})
        self.location = LocationFactory.create(**{
            'creator': self.user})
        self.observation = ObservationFactory.create(**{
            'creator': self.user,
            'location': self.location,
            'project': self.project,
            'category': self.category})

    def test_log_create(self):
        """Test when observation gets created."""
        log_count_init = LoggerHistory.objects.count()
        observation = ObservationFactory.create(**{
            'creator': self.user,
            'location': self.location,
            'project': self.project,
            'category': self.category})

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
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(observation.id)})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'Observation',
            'field': 'status',
            'value': observation.status})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_create_draft(self):
        """Test when observation gets created as a draft."""
        log_count_init = LoggerHistory.objects.count()
        ObservationFactory.create(**{
            'status': 'draft',
            'creator': self.user,
            'location': self.location,
            'project': self.project,
            'category': self.category})

        self.assertEqual(LoggerHistory.objects.count(), log_count_init)

    def test_log_create_from_draft_status(self):
        """Test when observation gets created from being a draft."""
        self.observation.status = 'draft'
        self.observation.save()
        log_count_init = LoggerHistory.objects.count()

        original_status = self.observation.status
        self.observation.status = 'pending'
        self.observation.save()

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
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(self.observation.id)})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'Observation',
            'field': 'status',
            'value': self.observation.status})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)
        self.assertEqual(history.status, original_status)

    def test_log_delete(self):
        """Test when observation gets deleted."""
        observation_id = self.observation.id
        log_count_init = LoggerHistory.objects.count()
        self.observation.delete()

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
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(observation_id)})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'class': 'Observation',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)

    def test_log_update_status(self):
        """Test when observation status changes."""
        log_count_init = LoggerHistory.objects.count()

        original_status = self.observation.status
        self.observation.status = 'review'
        self.observation.save()

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
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(self.observation.id)})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Observation',
            'field': 'status',
            'value': 'review'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)
        self.assertEqual(history.status, original_status)

        original_status = self.observation.status
        self.observation.status = 'pending'
        self.observation.save()

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
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(self.observation.id)})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Observation',
            'field': 'status',
            'value': 'pending'})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)
        self.assertEqual(history.status, original_status)

        original_status = self.observation.status
        self.observation.status = 'active'
        self.observation.save()

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
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(self.observation.id)})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Observation',
            'field': 'status',
            'value': 'active'})
        self.assertEqual(log_count, log_count_init + 3)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)
        self.assertEqual(history.status, original_status)

    def test_log_update_properties(self):
        """Test when observation properties changes."""
        log_count_init = LoggerHistory.objects.count()

        original_properties = self.observation.properties
        self.observation.properties = {'field': 'value'}
        self.observation.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(log_count, log_count_init + 1)

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
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(self.observation.id)})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Observation',
            'field': 'properties'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)
        self.assertEqual(history.properties, original_properties)

    def test_log_update_properties_when_draft(self):
        """Test when observation properties changes, but status is "draft"."""
        self.observation.status = 'draft'
        self.observation.save()
        log_count_init = LoggerHistory.objects.count()

        self.observation.properties
        self.observation.properties = {'field': 'value'}
        self.observation.save()

        self.assertEqual(LoggerHistory.objects.count(), log_count_init)
