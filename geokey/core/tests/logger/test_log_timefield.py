"""Tests for logger: model TimeField."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import (
    CategoryFactory,
    TimeFieldFactory,
)


class LogTimeFieldTest(TestCase):
    """Test model TimeField."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})
        self.timefield = TimeFieldFactory.create(**{
            'category': self.category})

    def test_log_create(self):
        """Test when time field gets created."""
        log_count_init = LoggerHistory.objects.count()
        field = TimeFieldFactory.create(**{
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
        self.assertEqual(log.field, {
            'id': str(field.id),
            'name': field.name,
            'type': 'TimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'Field'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
        """Test when time field gets deleted."""
        field_id = self.timefield.id
        field_name = self.timefield.name
        log_count_init = LoggerHistory.objects.count()
        self.timefield.delete()

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
        self.assertEqual(log.field, {
            'id': str(field_id),
            'name': field_name,
            'type': 'TimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'class': 'Field'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_name(self):
        """Test when name changes."""
        log_count_init = LoggerHistory.objects.count()
        self.timefield.name = '%s UPDATED' % self.timefield.name
        self.timefield.save()

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
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'name'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_status(self):
        """Test when status changes."""
        log_count_init = LoggerHistory.objects.count()

        self.timefield.status = 'inactive'
        self.timefield.save()

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
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'status',
            'value': self.timefield.status})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.timefield.status = 'active'
        self.timefield.save()

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
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'status',
            'value': self.timefield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_required(self):
        """Test when required setting changes."""
        log_count_init = LoggerHistory.objects.count()

        self.timefield.required = True
        self.timefield.save()

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
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'required',
            'value': str(self.timefield.required)})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.timefield.required = False
        self.timefield.save()

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
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'required',
            'value': str(self.timefield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)
