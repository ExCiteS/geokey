"""Tests for logger: model LookupField."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import (
    CategoryFactory,
    MultipleLookupFieldFactory,
)


class LogLookupFieldTest(TestCase):
    """Test model LookupField."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})
        self.multiplelookupfield = MultipleLookupFieldFactory.create(**{
            'category': self.category})

    def test_log_create(self):
        """Test when multiple lookup field gets created."""
        log_count_init = LoggerHistory.objects.count()
        field = MultipleLookupFieldFactory.create(**{
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
            'type': 'MultipleLookupField'})
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
        """Test when multiple lookup field gets deleted."""
        field_id = self.multiplelookupfield.id
        field_name = self.multiplelookupfield.name
        log_count_init = LoggerHistory.objects.count()
        self.multiplelookupfield.delete()

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
            'type': 'MultipleLookupField'})
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
        self.multiplelookupfield.name = '%s UPDATED' % (
            self.multiplelookupfield.name)
        self.multiplelookupfield.save()

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
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
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

        self.multiplelookupfield.status = 'inactive'
        self.multiplelookupfield.save()

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
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'status',
            'value': self.multiplelookupfield.status})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.multiplelookupfield.status = 'active'
        self.multiplelookupfield.save()

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
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'status',
            'value': self.multiplelookupfield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_required(self):
        """Test when required setting changes."""
        log_count_init = LoggerHistory.objects.count()

        self.multiplelookupfield.required = True
        self.multiplelookupfield.save()

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
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'required',
            'value': str(self.multiplelookupfield.required)})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.multiplelookupfield.required = False
        self.multiplelookupfield.save()

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
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.location, None)
        self.assertEqual(log.observation, None)
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'class': 'Field',
            'field': 'required',
            'value': str(self.multiplelookupfield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)
