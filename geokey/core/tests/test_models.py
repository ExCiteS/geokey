"""Tests for core models."""

from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import (
    CategoryFactory,
    TextFieldFactory,
    NumericFieldFactory,
    DateTimeFieldFactory,
    DateFieldFactory,
    TimeFieldFactory,
    LookupFieldFactory,
    MultipleLookupFieldFactory,
)
from geokey.subsets.tests.model_factories import SubsetFactory


from ..models import LoggerHistory


class LoggerHistoryTest(TestCase):
    """Test LoggerHistory."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})
        self.textfield = TextFieldFactory.create(**{
            'category': self.category})
        self.numericfield = NumericFieldFactory.create(**{
            'category': self.category})
        self.datetimefield = DateTimeFieldFactory.create(**{
            'category': self.category})
        self.datefield = DateFieldFactory.create(**{
            'category': self.category})
        self.timefield = TimeFieldFactory.create(**{
            'category': self.category})
        self.lookupfield = LookupFieldFactory.create(**{
            'category': self.category})
        self.multiplelookupfield = MultipleLookupFieldFactory.create(**{
            'category': self.category})
        self.subset = SubsetFactory.create(**{
            'creator': self.user,
            'project': self.project})

    # USERS
    def test_log_create_user(self):
        """Test when user gets created."""
        log_count_init = LoggerHistory.objects.count()
        UserFactory.create()
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

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(project.id),
            'name': project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete_project(self):
        """Test when project gets deleted."""
        project_id = self.project.id
        project_name = self.project.name
        log_count_init = LoggerHistory.objects.count()
        self.project.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(project_id),
            'name': project_name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, project_id)
        self.assertEqual(history.name, project_name)

    def test_log_update_project_name(self):
        """Test when project name changes."""
        log_count_init = LoggerHistory.objects.count()
        original_name = self.project.name
        self.project.name = '%s UPDATED' % self.project.name
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.project.name})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.name, original_name)

    def test_log_update_project_status(self):
        """Test when project status changes."""
        log_count_init = LoggerHistory.objects.count()

        original_status = self.project.status
        self.project.status = 'inactive'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.project.status})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.status, original_status)

        original_status = self.project.status
        self.project.status = 'active'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.project.status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.status, original_status)

    def test_log_update_project_isprivate(self):
        """Test when project privacy changes."""
        log_count_init = LoggerHistory.objects.count()

        original_isprivate = self.project.isprivate
        self.project.isprivate = False
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'isprivate',
            'value': str(self.project.isprivate)})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.isprivate, original_isprivate)

        original_isprivate = self.project.isprivate
        self.project.isprivate = True
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'isprivate',
            'value': str(self.project.isprivate)})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.isprivate, original_isprivate)

    def test_log_update_project_islocked(self):
        """Test when project locker changes."""
        log_count_init = LoggerHistory.objects.count()

        original_islocked = self.project.islocked
        self.project.islocked = True
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'islocked',
            'value': str(self.project.islocked)})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.islocked, original_islocked)

        original_islocked = self.project.islocked
        self.project.islocked = False
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'islocked',
            'value': str(self.project.islocked)})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.islocked, original_islocked)


    def test_log_update_project_contributing_permissions(self):
        """Test when project contributing permissions changes."""
        log_count_init = LoggerHistory.objects.count()

        original_everyone_contributes = self.project.everyone_contributes
        self.project.everyone_contributes = 'auth'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'everyone_contributes',
            'value': self.project.everyone_contributes})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(
            history.everyone_contributes,
            original_everyone_contributes)

        original_everyone_contributes = self.project.everyone_contributes
        self.project.everyone_contributes = 'false'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'everyone_contributes',
            'value': self.project.everyone_contributes})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(
            history.everyone_contributes,
            original_everyone_contributes)

        original_everyone_contributes = self.project.everyone_contributes
        self.project.everyone_contributes = 'true'
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'everyone_contributes',
            'value': self.project.everyone_contributes})
        self.assertEqual(log_count, log_count_init + 3)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(
            history.everyone_contributes,
            original_everyone_contributes)

    def test_log_update_project_geo_extent(self):
        """Test when project geo. extent changes."""
        log_count_init = LoggerHistory.objects.count()
        original_geographic_extent = self.project.geographic_extent
        self.project.geographic_extent = GEOSGeometry(
            '{"type": "Polygon","coordinates":'
            '[[[-0.505,51.682],[-0.53,51.327],'
            '[0.225,51.323],[0.167,51.667],[-0.505,51.682]]]}')
        self.project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'geographic_extent',
            'value': self.project.geographic_extent.json})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.project.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.project.id)
        self.assertEqual(history.geographic_extent, original_geographic_extent)

    # CATEGORIES
    def test_log_create_category(self):
        """Test when category gets created."""
        log_count_init = LoggerHistory.objects.count()
        category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(category.id),
            'name': category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete_category(self):
        """Test when category gets deleted."""
        category_id = self.category.id
        category_name = self.category.name
        log_count_init = LoggerHistory.objects.count()
        self.category.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(category_id),
            'name': category_name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, category_id)
        self.assertEqual(history.name, category_name)

    def test_log_update_category_name(self):
        """Test when category name changes."""
        log_count_init = LoggerHistory.objects.count()
        original_name = self.category.name
        self.category.name = '%s UPDATED' % self.category.name
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.category.name})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.name, original_name)

    def test_log_update_category_status(self):
        """Test when category status changes."""
        log_count_init = LoggerHistory.objects.count()

        original_status = self.category.status
        self.category.status = 'inactive'
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.category.status})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.status, original_status)

        original_status = self.category.status
        self.category.status = 'active'
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.category.status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.status, original_status)

    def test_log_update_category_default_status(self):
        """Test when category default status changes."""
        log_count_init = LoggerHistory.objects.count()

        original_default_status = self.category.default_status
        self.category.default_status = 'active'
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'default_status',
            'value': self.category.default_status})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.default_status, original_default_status)

        original_default_status = self.category.default_status
        self.category.default_status = 'pending'
        self.category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'default_status',
            'value': self.category.default_status})
        self.assertEqual(log_count, log_count_init + 2)
        history = self.category.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.category.id)
        self.assertEqual(history.default_status, original_default_status)

    # TEXT FIELDS
    def test_log_create_text_field(self):
        """Test when text field gets created."""
        log_count_init = LoggerHistory.objects.count()
        field = TextFieldFactory.create(**{
            'category': self.category})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(field.id),
            'name': field.name,
            'type': 'TextField'})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_text_field_name(self):
        """Test when text field name changes."""
        log_count_init = LoggerHistory.objects.count()
        self.textfield.name = '%s UPDATED' % self.textfield.name
        self.textfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.textfield.id),
            'name': self.textfield.name,
            'type': 'TextField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.textfield.name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_text_field_status(self):
        """Test when text field status changes."""
        log_count_init = LoggerHistory.objects.count()

        self.textfield.status = 'inactive'
        self.textfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.textfield.id),
            'name': self.textfield.name,
            'type': 'TextField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.textfield.status})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.textfield.status = 'active'
        self.textfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.textfield.id),
            'name': self.textfield.name,
            'type': 'TextField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.textfield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_text_field_required(self):
        """Test when text field required setting changes."""
        log_count_init = LoggerHistory.objects.count()

        self.textfield.required = True
        self.textfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.textfield.id),
            'name': self.textfield.name,
            'type': 'TextField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.textfield.required)})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.textfield.required = False
        self.textfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.textfield.id),
            'name': self.textfield.name,
            'type': 'TextField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.textfield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    # NUMERIC FIELDS
    def test_log_create_numeric_field(self):
        """Test when numeric field gets created."""
        log_count_init = LoggerHistory.objects.count()
        field = NumericFieldFactory.create(**{
            'category': self.category})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(field.id),
            'name': field.name,
            'type': 'NumericField'})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_numeric_field_name(self):
        """Test when numeric field name changes."""
        log_count_init = LoggerHistory.objects.count()
        self.numericfield.name = '%s UPDATED' % self.numericfield.name
        self.numericfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.numericfield.id),
            'name': self.numericfield.name,
            'type': 'NumericField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.numericfield.name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_numeric_field_status(self):
        """Test when numeric field status changes."""
        log_count_init = LoggerHistory.objects.count()

        self.numericfield.status = 'inactive'
        self.numericfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.numericfield.id),
            'name': self.numericfield.name,
            'type': 'NumericField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.numericfield.status})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.numericfield.status = 'active'
        self.numericfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.numericfield.id),
            'name': self.numericfield.name,
            'type': 'NumericField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.numericfield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_numeric_field_required(self):
        """Test when numeric field required setting changes."""
        log_count_init = LoggerHistory.objects.count()

        self.numericfield.required = True
        self.numericfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.numericfield.id),
            'name': self.numericfield.name,
            'type': 'NumericField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.numericfield.required)})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.numericfield.required = False
        self.numericfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.numericfield.id),
            'name': self.numericfield.name,
            'type': 'NumericField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.numericfield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    # DATE & TIME FIELDS
    def test_log_create_date_time_field(self):
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(field.id),
            'name': field.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_date_time_field_name(self):
        """Test when date & time field name changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.datetimefield.name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_date_time_field_status(self):
        """Test when date & time field status changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.datetimefield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_date_time_field_required(self):
        """Test when date & time field required setting changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datetimefield.id),
            'name': self.datetimefield.name,
            'type': 'DateTimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.datetimefield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    # DATE FIELDS
    def test_log_create_date_field(self):
        """Test when date field gets created."""
        log_count_init = LoggerHistory.objects.count()
        field = DateFieldFactory.create(**{
            'category': self.category})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(field.id),
            'name': field.name,
            'type': 'DateField'})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_date_field_name(self):
        """Test when date field name changes."""
        log_count_init = LoggerHistory.objects.count()
        self.datefield.name = '%s UPDATED' % self.lookupfield.name
        self.datefield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datefield.id),
            'name': self.datefield.name,
            'type': 'DateField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.datefield.name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_date_field_status(self):
        """Test when date field status changes."""
        log_count_init = LoggerHistory.objects.count()

        self.datefield.status = 'inactive'
        self.datefield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datefield.id),
            'name': self.datefield.name,
            'type': 'DateField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.datefield.status})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.datefield.status = 'active'
        self.datefield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datefield.id),
            'name': self.datefield.name,
            'type': 'DateField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.datefield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_date_field_required(self):
        """Test when date field required setting changes."""
        log_count_init = LoggerHistory.objects.count()

        self.datefield.required = True
        self.datefield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datefield.id),
            'name': self.datefield.name,
            'type': 'DateField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.datefield.required)})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.datefield.required = False
        self.datefield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.datefield.id),
            'name': self.datefield.name,
            'type': 'DateField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.datefield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    # TIME FIELDS
    def test_log_create_time_field(self):
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(field.id),
            'name': field.name,
            'type': 'TimeField'})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_time_field_name(self):
        """Test when time field name changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.timefield.name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_time_field_status(self):
        """Test when time field status changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.timefield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_time_field_required(self):
        """Test when time field required setting changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.timefield.id),
            'name': self.timefield.name,
            'type': 'TimeField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.timefield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    # LOOKUP FIELDS
    def test_log_create_lookup_field(self):
        """Test when lookup field gets created."""
        log_count_init = LoggerHistory.objects.count()
        field = LookupFieldFactory.create(**{
            'category': self.category})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(field.id),
            'name': field.name,
            'type': 'LookupField'})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_lookup_field_name(self):
        """Test when lookup field name changes."""
        log_count_init = LoggerHistory.objects.count()
        self.lookupfield.name = '%s UPDATED' % self.lookupfield.name
        self.lookupfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.lookupfield.id),
            'name': self.lookupfield.name,
            'type': 'LookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.lookupfield.name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_lookup_field_status(self):
        """Test when lookup field status changes."""
        log_count_init = LoggerHistory.objects.count()

        self.lookupfield.status = 'inactive'
        self.lookupfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.lookupfield.id),
            'name': self.lookupfield.name,
            'type': 'LookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.lookupfield.status})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.lookupfield.status = 'active'
        self.lookupfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.lookupfield.id),
            'name': self.lookupfield.name,
            'type': 'LookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.lookupfield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_lookup_field_required(self):
        """Test when lookup field required setting changes."""
        log_count_init = LoggerHistory.objects.count()

        self.lookupfield.required = True
        self.lookupfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.lookupfield.id),
            'name': self.lookupfield.name,
            'type': 'LookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.lookupfield.required)})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        self.lookupfield.required = False
        self.lookupfield.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.lookupfield.id),
            'name': self.lookupfield.name,
            'type': 'LookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.lookupfield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    # MULTIPLE LOOKUP FIELDS
    def test_log_create_multiple_lookup_field(self):
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(field.id),
            'name': field.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_multiple_lookup_field_name(self):
        """Test when multiple lookup field name changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.multiplelookupfield.name})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_multiple_lookup_field_status(self):
        """Test when multiple lookup field status changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'status',
            'value': self.multiplelookupfield.status})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    def test_log_update_multiple_lookup_field_required(self):
        """Test when multiple lookup field required setting changes."""
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
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
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, {
            'id': str(self.multiplelookupfield.id),
            'name': self.multiplelookupfield.name,
            'type': 'MultipleLookupField'})
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'required',
            'value': str(self.multiplelookupfield.required)})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

    # SUBSETS
    def test_log_create_subset(self):
        """Test when category gets created."""
        log_count_init = LoggerHistory.objects.count()
        subset = SubsetFactory.create(**{
            'creator': self.user,
            'project': self.project})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.subset, {
            'id': str(subset.id),
            'name': subset.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'created'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_update_subset_name(self):
        """Test when category name changes."""
        log_count_init = LoggerHistory.objects.count()
        original_name = self.subset.name
        self.subset.name = '%s UPDATED' % self.subset.name
        self.subset.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.subset, {
            'id': str(self.subset.id),
            'name': self.subset.name})
        self.assertEqual(log.category, None)
        self.assertEqual(log.field, None)
        self.assertEqual(log.action, {
            'id': 'updated',
            'field': 'name',
            'value': self.subset.name})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.subset.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.subset.id)
        self.assertEqual(history.name, original_name)
