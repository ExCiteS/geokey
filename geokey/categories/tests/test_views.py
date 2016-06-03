# -*- coding: utf-8 -*-
"""Tests for views of categories."""

import json

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.messages.storage.fallback import FallbackStorage

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from geokey.projects.tests.model_factories import UserFactory, ProjectFactory
from geokey.core.tests.helpers.image_helpers import get_image

from .model_factories import (
    CategoryFactory, TextFieldFactory, NumericFieldFactory, DateFieldFactory,
    DateTimeFieldFactory, LookupFieldFactory, LookupValueFactory,
    MultipleLookupFieldFactory, MultipleLookupValueFactory
)

from ..models import Category, Field, LookupValue, MultipleLookupValue
from ..views import (
    CategoryOverview, CategoryDelete, FieldSettings, FieldDelete,
    CategoryUpdate, FieldUpdate, FieldLookupsUpdate, FieldLookups,
    SingleCategory, CategoryCreate, CategorySettings,
    FieldCreate, CategoryList, CategoryDisplay, FieldsReorderView
)

# ############################################################################
#
# ADMIN PAGES
#
# ############################################################################


class CategoryListTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

    def get(self, user):
        view = CategoryList.as_view()
        url = reverse('admin:category_list', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(request, project_id=self.project.id).render()

    def test_get_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )


class CategoryOverviewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(**{'project': self.project})

    def get(self, user):
        view = CategoryOverview.as_view()
        url = reverse('admin:category_overview', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id,
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

    def test_get_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )


class CategoryCreateTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

    def get(self, user):
        view = CategoryCreate.as_view()
        url = reverse('admin:category_create', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(request, project_id=self.project.id).render()

    def post(self, user, data):
        view = CategoryCreate.as_view()
        url = reverse('admin:category_create', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.post(url, data, follow=True)

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        request.user = user
        return view(request, project_id=self.project.id)

    def test_get_create_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_create_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_create_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )


class CategoryDisplayTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{
                'project': self.project,
                'symbol': get_image(file_name='test_category_symbol_1.png')
            }
        )

    def tearDown(self):
        for category in Category.objects.all():
            if category.symbol is not None:
                category.symbol.delete()

    def get(self, user):
        view = CategoryDisplay.as_view()
        url = reverse('admin:category_display', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id).render()

    def post(self, user, clear_symbol='false'):
        self.data = {
            'colour': '#222222',
            'symbol': get_image(
                file_name='test_category_symbol_2.png'
            ) if clear_symbol == 'false' else None,
            'clear-symbol': clear_symbol
        }
        view = CategoryDisplay.as_view()
        url = reverse('admin:category_display', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.post(url, self.data)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id).render()

    def test_get_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

    def test_update_with_admin(self):
        response = self.post(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ref = Category.objects.get(pk=self.category.id)
        self.assertEqual(ref.colour, self.data.get('colour'))
        self.assertNotEqual(ref.symbol, self.category.symbol)

    def test_update_clear_symbol_with_admin(self):
        response = self.post(self.admin, clear_symbol='true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ref = Category.objects.get(pk=self.category.id)
        self.assertEqual(ref.colour, self.data.get('colour'))
        self.assertFalse(bool(ref.symbol))

    def test_update_with_contributor(self):
        response = self.post(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertNotEqual(ref.colour, self.data.get('colour'))
        self.assertEqual(ref.symbol, self.category.symbol)

    def test_update_with_non_member(self):
        response = self.post(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertNotEqual(ref.colour, self.data.get('colour'))
        self.assertEqual(ref.symbol, self.category.symbol)


class CategorySettingsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project})

    def get(self, user):
        view = CategorySettings.as_view()
        url = reverse('admin:category_settings', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id).render()

    def post(self, user, display_field=None, expiry_field=None):
        self.data = {
            'name': 'Cat Name',
            'description': 'Cat description',
            'default_status': 'active',
            'display_field': display_field,
            'expiry_field': expiry_field
        }
        view = CategorySettings.as_view()
        url = reverse('admin:category_settings', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.post(url, self.data)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

    def test_get_settings_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_settings_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_settings_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

    def test_update_settings_with_admin(self):
        response = self.post(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertEqual(ref.name, self.data.get('name'))
        self.assertEqual(ref.description, self.data.get('description'))
        self.assertEqual(ref.default_status, self.data.get('default_status'))

    def test_update_settings_with_displayfield(self):
        field_1 = TextFieldFactory.create(**{'category': self.category})
        field_2 = TextFieldFactory.create(**{'category': self.category})

        self.category.display_field = field_1
        self.category.save()

        response = self.post(self.admin, display_field=field_2.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertEqual(ref.name, self.data.get('name'))
        self.assertEqual(ref.description, self.data.get('description'))
        self.assertEqual(ref.default_status, self.data.get('default_status'))
        self.assertEqual(ref.display_field, field_2)

    def test_update_settings_when_clearing_displayfield(self):
        field = TextFieldFactory.create(**{'category': self.category})

        self.category.display_field = field
        self.category.save()

        response = self.post(self.admin, display_field=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertEqual(ref.name, self.data.get('name'))
        self.assertEqual(ref.description, self.data.get('description'))
        self.assertEqual(ref.default_status, self.data.get('default_status'))
        self.assertEqual(ref.display_field, None)

    def test_update_settings_with_expiryfield(self):
        field_1 = DateFieldFactory.create(**{'category': self.category})
        field_2 = DateFieldFactory.create(**{'category': self.category})

        self.category.expiry_field = field_1
        self.category.save()

        response = self.post(self.admin, expiry_field=field_2.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertEqual(ref.name, self.data.get('name'))
        self.assertEqual(ref.description, self.data.get('description'))
        self.assertEqual(ref.default_status, self.data.get('default_status'))
        self.assertEqual(ref.expiry_field, field_2)

    def test_update_settings_when_clearing_expiryfield(self):
        field = DateFieldFactory.create(**{'category': self.category})

        self.category.expiry_field = field
        self.category.save()

        response = self.post(self.admin, expiry_field=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertEqual(ref.name, self.data.get('name'))
        self.assertEqual(ref.description, self.data.get('description'))
        self.assertEqual(ref.default_status, self.data.get('default_status'))
        self.assertEqual(ref.expiry_field, None)

    def test_update_settings_when_field_for_expiryfield_is_wrong(self):
        field_1 = DateFieldFactory.create(**{'category': self.category})
        field_2 = TextFieldFactory.create(**{'category': self.category})

        self.category.expiry_field = field_1
        self.category.save()

        response = self.post(self.admin, expiry_field=field_2.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )
        self.assertContains(
            response,
            'Only `Date and Time` and `Date` fields can be used.'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertEqual(ref.name, self.data.get('name'))
        self.assertEqual(ref.description, self.data.get('description'))
        self.assertEqual(ref.default_status, self.data.get('default_status'))
        self.assertEqual(ref.expiry_field, field_1)

    def test_update_settings_with_non_member(self):
        response = self.post(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertNotEqual(ref.name, self.data.get('name'))
        self.assertNotEqual(ref.description, self.data.get('description'))
        self.assertNotEqual(
            ref.default_status, self.data.get('default_status'))

    def test_update_settings_with_contributor(self):
        response = self.post(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Category.objects.get(pk=self.category.id)
        self.assertNotEqual(ref.name, self.data.get('name'))
        self.assertNotEqual(ref.description, self.data.get('description'))
        self.assertNotEqual(
            ref.default_status, self.data.get('default_status'))


class CategoryDeleteTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project})

    def get(self, user):
        view = CategoryDelete.as_view()
        url = reverse('admin:category_delete', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.get(url)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id)

    def test_delete_with_admin(self):
        response = self.get(self.admin)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

        try:
            Category.objects.get(pk=self.category.id)
        except Category.DoesNotExist:
            pass
        else:
            self.fail('Category not deleted.')

    def test_delete_with_admin_on_locked_project(self):
        self.project.islocked = True
        self.project.save()

        response = self.get(self.admin)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

        try:
            Category.objects.get(pk=self.category.id)
        except Category.DoesNotExist:
            self.fail('Category has been deleted.')

    def test_delete_with_contributor(self):
        response = self.get(self.contributor).render()
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        try:
            Category.objects.get(pk=self.category.id)
        except Category.DoesNotExist:
            self.fail('Category has been deleted.')

    def test_delete_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

        try:
            Category.objects.get(pk=self.category.id)
        except Category.DoesNotExist:
            self.fail('Category has been deleted.')


class FieldCreateTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project})

    def get(self, user):
        view = FieldCreate.as_view()
        url = reverse('admin:category_field_create', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id).render()

    def post(self, user, data):
        view = FieldCreate.as_view()
        url = reverse('admin:category_field_create', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.post(url, data)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id)

    def test_get_create_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_post_create_with_admin(self):
        data = {
            'name': 'Test name',
            'description': 'Test description',
            'required': False,
            'type': 'TextField'
        }
        response = self.post(self.admin, data)
        self.assertEquals(type(response), HttpResponseRedirect)
        self.assertEquals(Field.objects.count(), 1)

    def test_post_create_with_hebrew_field_name(self):
        data = {
            'name': 'צַדִי, צדיק',
            'description': 'Test description',
            'required': False,
            'type': 'TextField'
        }
        response = self.post(self.admin, data)
        self.assertEquals(type(response), HttpResponseRedirect)
        self.assertEquals(Field.objects.count(), 1)
        field = self.category.fields.all()[0]
        self.assertEquals(field.key, 'key')

    def test_post_create_with_admin_on_locked_projects(self):
        self.project.islocked = True
        self.project.save()

        data = {
            'name': 'Test name',
            'description': 'Test description',
            'required': False,
            'type': 'TextField'
        }
        response = self.post(self.admin, data)
        self.assertEquals(type(response), HttpResponseRedirect)
        self.assertEquals(Field.objects.count(), 0)

    def test_post_create_with_existing_name(self):
        TextFieldFactory.create(**{
            'category': self.category,
            'name': 'Test Name',
            'key': 'test-name'
        })

        data = {
            'name': 'Test name',
            'description': 'Test description',
            'required': False,
            'type': 'TextField'
        }
        response = self.post(self.admin, data)
        self.assertEquals(type(response), HttpResponseRedirect)
        self.assertEquals(Field.objects.count(), 2)

    def test_post_create_numeric_field(self):
        data = {
            'name': 'Test name',
            'description': 'Test description',
            'required': False,
            'type': 'NumericField',
            'minval': 10
        }
        response = self.post(self.admin, data)
        self.assertEquals(type(response), HttpResponseRedirect)

    def test_post_create_with_admin_and_long_name(self):
        data = {
            'name': 'Test name that is really long more than 30 chars',
            'description': 'Test description',
            'required': False,
            'type': 'TextField'
        }
        response = self.post(self.admin, data)
        self.assertEquals(type(response), HttpResponseRedirect)

    def test_get_create_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_create_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )


class FieldSettingsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project})
        self.field = TextFieldFactory.create(
            **{'category': self.category})

    def get(self, user):
        view = FieldSettings.as_view()
        url = reverse('admin:category_field_settings', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id,
            'field_id': self.field.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=self.field.id).render()

    def post(self, user):
        self.data = {
            'name': 'Field name',
            'description': 'Field description',
            'required': True
        }
        view = FieldSettings.as_view()
        url = reverse('admin:category_field_settings', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id,
            'field_id': self.field.id
        })
        request = self.factory.post(url, self.data)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=self.field.id).render()

    def test_get_settings_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_settings_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_settings_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

    def test_update_settings_with_admin(self):
        response = self.post(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Field.objects.get(pk=self.field.id)
        self.assertEqual(ref.name, self.data.get('name'))
        self.assertEqual(ref.description, self.data.get('description'))
        self.assertTrue(ref.required)

    def test_update_settings_with_contributor(self):
        response = self.post(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Field.objects.get(pk=self.field.id)
        self.assertNotEqual(ref.name, self.data.get('name'))
        self.assertNotEqual(ref.description, self.data.get('description'))
        self.assertFalse(ref.required)

    def test_update_settings_with_non_member(self):
        response = self.post(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

        ref = Field.objects.get(pk=self.field.id)
        self.assertNotEqual(ref.name, self.data.get('name'))
        self.assertNotEqual(ref.description, self.data.get('description'))
        self.assertFalse(ref.required)

    def test_update_numeric_settings_with_non_member(self):
        self.field = NumericFieldFactory.create(
            **{'category': self.category})

        response = self.post(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Field.objects.get(pk=self.field.id)
        self.assertEqual(ref.name, self.data.get('name'))
        self.assertEqual(ref.description, self.data.get('description'))
        self.assertTrue(ref.required)


class FieldDeleteTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project})
        self.field = TextFieldFactory.create(
            **{'category': self.category})

        self.display_field = TextFieldFactory.create(
            **{'category': self.category})
        self.category.display_field = self.display_field
        self.expiry_field = DateFieldFactory.create(**{
            'category': self.category
        })
        self.category.expiry_field = self.expiry_field
        self.category.save()

    def get(self, user, field):
        view = FieldDelete.as_view()
        url = reverse('admin:category_field_delete', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id,
            'field_id': field.id
        })
        request = self.factory.get(url)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=field.id)

    def test_delete_with_admin(self):
        response = self.get(self.admin, self.field)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

        try:
            Field.objects.get(pk=self.field.id)
        except Field.DoesNotExist:
            pass
        else:
            self.fail('Field not deleted.')

    def test_delete_with_admin_on_locked_project(self):
        self.project.islocked = True
        self.project.save()

        response = self.get(self.admin, self.field)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

        try:
            Field.objects.get(pk=self.field.id)
        except Field.DoesNotExist:
            self.fail('Field has been deleted.')

    def test_delete_with_admin_when_field_is_set_as_display_field(self):
        response = self.get(self.admin, self.display_field)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

        try:
            Field.objects.get(pk=self.field.id)
        except Field.DoesNotExist:
            self.fail('Field has been deleted.')

    def test_delete_with_admin_when_field_is_set_as_expiry_field(self):
        response = self.get(self.admin, self.expiry_field)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

        try:
            Field.objects.get(pk=self.field.id)
        except Field.DoesNotExist:
            self.fail('Field has been deleted.')

    def test_delete_with_contributor(self):
        response = self.get(self.contributor, self.field).render()
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        try:
            Field.objects.get(pk=self.field.id)
        except Field.DoesNotExist:
            self.fail('Field has been deleted.')

    def test_delete_with_non_member(self):
        response = self.get(self.non_member, self.field)
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

        try:
            Field.objects.get(pk=self.field.id)
        except Field.DoesNotExist:
            self.fail('Category has been deleted.')

# ############################################################################
#
# AJAX API
#
# ############################################################################


class CategoryAjaxTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def _get(self, user):
        url = reverse(
            'ajax:category',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id
            }
        )
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        view = CategoryUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id
        ).render()

    def _put(self, data, user):
        url = reverse(
            'ajax:category',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = CategoryUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id
        ).render()

    def test_get_with_admin(self):
        response = self._get(self.admin)
        self.assertEqual(response.status_code, 200)

    def test_get_with_contributor(self):
        response = self._get(self.contributor)
        self.assertEqual(response.status_code, 403)

    def test_get_with_non_member(self):
        response = self._get(self.non_member)
        self.assertEqual(response.status_code, 404)

    def test_update_not_existing_type(self):
        url = reverse(
            'ajax:category',
            kwargs={
                'project_id': self.project.id,
                'category_id': 2376
            }
        )
        request = self.factory.put(url, {'status': 'inactive'})
        force_authenticate(request, user=self.admin)
        view = CategoryUpdate.as_view()
        response = view(
            request,
            project_id=self.project.id,
            category_id=2376
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_update_wrong_status(self):
        response = self._put({'status': 'bockwurst'}, self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )

    def test_update_description_with_admin(self):
        response = self._put({'description': 'new description'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            'new description'
        )

    def test_update_status_with_admin(self):
        response = self._put({'status': 'inactive'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            'inactive'
        )

    def test_update_description_with_contributor(self):
        response = self._put(
            {'description': 'new description'}, self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            self.active_type.description
        )

    def test_update_status_with_contributor(self):
        response = self._put(
            {'status': 'inactive'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )

    def test_update_description_with_non_member(self):
        response = self._put(
            {'description': 'new description'},
            self.non_member
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            self.active_type.description
        )

    def test_update_status_with_contributor_non_member(self):
        response = self._put(
            {'status': 'inactive'},
            self.non_member
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )


class ReorderFieldsTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.category = CategoryFactory.create()

        self.field_0 = TextFieldFactory.create(
            **{'category': self.category})
        self.field_1 = TextFieldFactory.create(
            **{'category': self.category})
        self.field_2 = TextFieldFactory.create(
            **{'category': self.category})
        self.field_3 = TextFieldFactory.create(
            **{'category': self.category})
        self.field_4 = TextFieldFactory.create(
            **{'category': self.category})

    def test_reorder(self):
        url = reverse(
            'ajax:category_fields_reorder',
            kwargs={
                'project_id': self.category.project.id,
                'category_id': self.category.id
            }
        )

        data = [
            self.field_4.id, self.field_0.id, self.field_2.id, self.field_1.id,
            self.field_3.id
        ]

        request = self.factory.post(
            url, json.dumps({'order': data}), content_type='application/json')
        force_authenticate(request, user=self.category.project.creator)
        view = FieldsReorderView.as_view()
        response = view(
            request,
            project_id=self.category.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 200)

        fields = self.category.fields.all()

        self.assertTrue(fields.ordered)
        self.assertEqual(fields[0], self.field_4)
        self.assertEqual(fields[1], self.field_0)
        self.assertEqual(fields[2], self.field_2)
        self.assertEqual(fields[3], self.field_1)
        self.assertEqual(fields[4], self.field_3)

    def test_reorder_with_false_field(self):
        url = reverse(
            'ajax:category_fields_reorder',
            kwargs={
                'project_id': self.category.project.id,
                'category_id': self.category.id
            }
        )

        data = [
            self.field_4.id, self.field_0.id, self.field_2.id, self.field_1.id,
            655123135135
        ]

        request = self.factory.post(
            url, json.dumps({'order': data}), content_type='application/json')
        force_authenticate(request, user=self.category.project.creator)
        view = FieldsReorderView.as_view()
        response = view(
            request,
            project_id=self.category.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 400)

        fields = self.category.fields.all()

        self.assertTrue(fields.ordered)
        self.assertEqual(fields[0].order, 0)
        self.assertEqual(fields[1].order, 0)
        self.assertEqual(fields[2].order, 0)
        self.assertEqual(fields[3].order, 0)
        self.assertEqual(fields[4].order, 0)


class UpdateFieldTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.category = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

        self.field = TextFieldFactory(**{
            'category': self.category
        })

    def _put(self, data, user):
        url = reverse(
            'ajax:category_field',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id,
                'field_id': self.field.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = FieldUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=self.field.id
        ).render()

    def test_update_non_existing_field(self):
        url = reverse(
            'ajax:category_field',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id,
                'field_id': 554454545
            }
        )
        request = self.factory.put(url, {'description': 'new description'})
        force_authenticate(request, user=self.admin)
        view = FieldUpdate.as_view()
        response = view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=554454545
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_update_status_with_admin(self):
        response = self._put({'status': 'inactive'}, self.admin)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'inactive'
        )

    def test_update_numeric_status_with_admin(self):
        self.field = NumericFieldFactory(**{
            'category': self.category
        })
        response = self._put({'status': 'inactive'}, self.admin)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'inactive'
        )

    def test_update_status_with_contributor(self):
        response = self._put({'status': 'inactive'}, self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'active'
        )

    def test_update_status_with_non_member(self):
        response = self._put({'status': 'inactive'}, self.non_member)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'active'
        )

    def test_update_wrong_status_with_admin(self):
        response = self._put({'status': 'bla'}, self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'active'
        )


class UpdateNumericField(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.category = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

        self.field = NumericFieldFactory(**{
            'category': self.category
        })

    def _put(self, data, user):
        url = reverse(
            'ajax:category_field',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id,
                'field_id': self.field.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = FieldUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=self.field.id
        ).render()

    def test_update_numericfield_description_with_admin(self):
        response = self._put({'description': 'new description'}, self.admin)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).description, 'new description'
        )


class AddLookupValueTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def tearDown(self):
        for lookup_value in LookupValue.objects.all():
            if lookup_value.symbol is not None:
                lookup_value.symbol.delete()

    def test_add_lookupvalue_with_admin(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 1)

    def test_add_lookupvalue_to_not_existing_field(self):
        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': 32874893274
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=32874893274
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_add_lookupvalue_to_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'category': self.active_type
        })
        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': num_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=num_field.id
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_add_lookupvalue_when_project_is_locked(self):
        self.project.islocked = True
        self.project.save()

        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id
        ).render()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 0)


class UpdateLookupValues(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def tearDown(self):
        for lookup_value in LookupValue.objects.all():
            if lookup_value.symbol is not None:
                lookup_value.symbol.delete()

    def test_update_lookupvalue_with_admin(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = LookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.post(url, {'name': 'New Name'})
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            LookupValue.objects.get(pk=lookup_value.id).name,
            'New Name'
        )

    def test_update_lookupvalue_when_adding_a_symbol(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = LookupValueFactory(**{
            'field': lookup_field,
            'symbol': None
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )

        data = {
            'symbol': get_image(
                file_name='test_lookupvalue_symbol.png'
            ),
            'clear-symbol': 'false'
        }

        request = self.factory.post(url, data)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 200)
        ref = LookupValue.objects.get(pk=lookup_value.id)
        self.assertNotEqual(ref.symbol, lookup_value.symbol)
        ref.symbol.delete()

    def test_update_lookupvalue_when_removing_a_symbol(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = LookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )

        data = {
            'symbol': None,
            'clear-symbol': 'true'
        }

        request = self.factory.post(url, data)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 200)
        ref = LookupValue.objects.get(pk=lookup_value.id)
        self.assertFalse(bool(ref.symbol))

    def test_update_lookupvalue_from_not_existing_field(self):
        lookup_value = LookupValueFactory()

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': 45455,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.post(url, {'name': 'New Name'})
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=45455,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_update_not_exisiting_lookupvalue(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.post(url, {'name': 'New Name'})
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_update_lookupvalue_from_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': num_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.post(url, {'name': 'New Name'})
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=num_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_update_lookupvalue_when_project_is_locked(self):
        self.project.islocked = True
        self.project.save()

        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = LookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.post(url, {'name': 'New Name'})
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 400)

    def test_remove_lookupvalue_with_admin(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = LookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            len(lookup_field.lookupvalues.filter(status='active')), 0
        )

    def test_remove_lookupvalue_from_not_existing_field(self):
        lookup_value = LookupValueFactory()

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': 45455,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=45455,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_not_exisiting_lookupvalue(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_lookupvalue_from_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': num_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=num_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_lookupvalue_when_project_is_locked(self):
        self.project.islocked = True
        self.project.save()

        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = LookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 1)


class AddMutipleLookupValueTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def test_add_lookupvalue_with_admin(self):
        lookup_field = MultipleLookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 1)

    def test_add_lookupvalue_when_project_is_locked(self):
        self.project.islocked = True
        self.project.save()

        lookup_field = MultipleLookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id
        ).render()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 0)


class RemoveMultipleLookupValues(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def tearDown(self):
        for lookup_value in MultipleLookupValue.objects.all():
            if lookup_value.symbol is not None:
                lookup_value.symbol.delete()

    def test_remove_lookupvalue_with_admin(self):
        lookup_field = MultipleLookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = MultipleLookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            len(lookup_field.lookupvalues.filter(status='active')), 0
        )

    def test_remove_lookupvalue_from_not_existing_field(self):
        lookup_value = MultipleLookupValueFactory.create()

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': 45455,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=45455,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_not_exisiting_lookupvalue(self):
        lookup_field = MultipleLookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_lookupvalue_from_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': num_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=num_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_lookupvalue_when_project_is_locked(self):
        self.project.islocked = True
        self.project.save()

        lookup_field = MultipleLookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = MultipleLookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 1)


# ############################################################################
#
# PUBLIC API
#
# ############################################################################

class SingleCategoryApiTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory(**{
            'status': 'active',
            'project': self.project
        })
        TextFieldFactory.create(**{
            'key': 'key_1',
            'category': self.category
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'category': self.category
        })
        self.inactive_field = TextFieldFactory.create(**{
            'key': 'key_3',
            'category': self.category,
            'status': 'inactive'
        })
        lookup_field = LookupFieldFactory(**{
            'key': 'key_4',
            'category': self.category
        })
        LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        LookupValueFactory(**{
            'name': 'Kermit',
            'field': lookup_field
        })
        LookupValueFactory(**{
            'name': 'Gonzo',
            'field': lookup_field,
            'status': 'inactive'
        })
        lookup_field = MultipleLookupFieldFactory(**{
            'key': 'key_5',
            'category': self.category
        })
        DateTimeFieldFactory.create(**{
            'key': 'key_6',
            'category': self.category
        })

    def tearDown(self):
        for lookup_value in LookupValue.objects.all():
            if lookup_value.symbol is not None:
                lookup_value.symbol.delete()

    def _get(self, user):
        url = reverse(
            'api:category',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id
            }
        )
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        view = SingleCategory.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

    def test_get_category_with_admin(self):
        response = self._get(self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Gonzo")
        self.assertNotContains(response, self.inactive_field.name)

    def test_get_category_with_contributor(self):
        response = self._get(self.contributor)
        self.assertEqual(response.status_code, 200)

    def test_get_category_with_non_member(self):
        response = self._get(self.non_member)
        self.assertEqual(response.status_code, 404)
