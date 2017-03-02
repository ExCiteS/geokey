from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.contributions.tests.model_factories import (
    ObservationFactory,
    LocationFactory
)


class LogObservationTest(TestCase):
    """Test model Observation."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'project': self.project,
            'creator': self.user})
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'category': self.category,
            'creator': self.user})
        self.location = LocationFactory.create()

    def test_log_create(self):
        """Test when observation gets created."""
        log_count_init = LoggerHistory.objects.count()
        observation = ObservationFactory.create(**{
            'project': self.project,
            'category': self.category,
            'creator': self.user,
            'location': self.location})
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
        self.assertEqual(log.subset, None)
        self.assertEqual(log.observation, {'id': str(observation.id)})
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'Observation'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
        """Test when observation gets deleted."""
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
        self.assertEqual(log.subset, None)
        self.assertEqual(log.observation, {'id': str(self.observation.id)})
        self.assertEqual(log.action, {
            'id': 'deleted',
            'class': 'Observation',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)

    def test_log_update_status(self):
        """Test when observation status gets cchanged."""
        log_count_init = LoggerHistory.objects.count()
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
        self.assertEqual(log.subset, None)
        self.assertEqual(log.observation, {'id': str(self.observation.id)})
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Observation',
            'field': 'status',
            'value': 'review'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)

        self.observation.status = 'draft'
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
        self.assertEqual(log.subset, None)
        self.assertEqual(log.observation, {'id': str(self.observation.id)})
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Observation',
            'field': 'status',
            'value': 'draft'})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)

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
        self.assertEqual(log.subset, None)
        self.assertEqual(log.observation, {'id': str(self.observation.id)})
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Observation',
            'field': 'status',
            'value': 'pending'})
        self.assertEqual(log_count, log_count_init + 3)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)

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
        self.assertEqual(log.subset, None)
        self.assertEqual(log.observation, {'id': str(self.observation.id)})
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Observation',
            'field': 'status',
            'value': 'active'})
        self.assertEqual(log_count, log_count_init + 4)
        history = self.observation.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.observation.id)
