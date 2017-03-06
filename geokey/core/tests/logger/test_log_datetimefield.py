"""Tests for logger: model DateTimeField."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import (
    CategoryFactory,
    DateTimeFieldFactory,
)


class LogDateTimeTest(TestCase):
    """Test model DateTimeField."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})
        self.datetimefield = DateTimeFieldFactory.create(**{
            'category': self.category})

    def test_log_create(self):
        """Test when date & time field gets created."""
        log_count_init = LoggerHistory.objects.count()
        field = DateTimeFieldFactory.create(**{
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
            'type': 'DateTimeField'})
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
        """Test when date & time field gets deleted."""
        field_id = self.datetimefield.id
        field_name = self.datetimefield.name
        log_count_init = LoggerHistory.objects.count()
        self.datetimefield.delete()

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
            'type': 'DateTimeField'})
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
        self.datetimefield.name = '%s UPDATED' % self.datetimefield.name
        self.datetimefield.save()

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
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
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

        self.datetimefield.status = 'inactive'
        self.datetimefield.save()

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
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'status',
            'value': self.datetimefield.status})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.datetimefield.status = 'active'
        self.datetimefield.save()

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
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'status',
            'value': self.datetimefield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_required(self):
        """Test when required setting changes."""
        log_count_init = LoggerHistory.objects.count()

        self.datetimefield.required = True
        self.datetimefield.save()

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
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'required',
            'value': str(self.datetimefield.required)})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.datetimefield.required = False
        self.datetimefield.save()

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
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'required',
            'value': str(self.datetimefield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)
