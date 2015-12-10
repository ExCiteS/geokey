import json

from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.contrib.messages import get_messages

from geokey import version
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory

from .model_factories import SubsetFactory
from ..models import Subset
from ..views import (
    SubsetOverview,
    SubsetCreate,
    SubsetSettings,
    SubsetData,
    SubsetDelete
)


class SubsetOverviewTest(TestCase):
    def setUp(self):
        self.view = SubsetOverview.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser should redirect to the login
        pages
        """
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Accessing the view with normal user should render the page with an
        error message
        """
        user = UserFactory.create()
        project = ProjectFactory.create()

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'subsets/subsets_overview.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_admin(self):
        """
        Accessing the view with project admin should render the page
        """
        project = ProjectFactory.create()
        user = project.creator

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'subsets/subsets_overview.html',
            {
                'project': project,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


class SubsetCreateTest(TestCase):
    def setUp(self):
        self.view = SubsetCreate.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser should redirect to the login
        pages
        """
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_anonymous(self):
        """
        Updating with AnonymousUser should redirect to the login page
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'description': 'Description',
        }
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(0, Subset.objects.count())

    def test_get_with_user(self):
        """
        Accessing the view with normal user should render the page with an
        error message
        """
        user = UserFactory.create()
        project = ProjectFactory.create()

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'subsets/subsets_create.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_user(self):
        """
        Updating with normal user should render the page with an
        error message
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'description': 'Description',
        }

        user = UserFactory.create()
        project = ProjectFactory.create()

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'subsets/subsets_create.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        self.assertEqual(0, Subset.objects.count())

    def test_get_with_admin(self):
        """
        Accessing the view with project admin should render the page
        """
        project = ProjectFactory.create()
        user = project.creator

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'subsets/subsets_create.html',
            {
                'project': project,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_admin(self):
        """
        Updating with project admin should create the subset and redirect to
        the subset data page.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'description': 'Description',
        }

        project = ProjectFactory.create()
        user = project.creator

        self.request.user = user
        response = self.view(self.request, project_id=project.id)

        self.assertEqual(1, Subset.objects.count())
        subset = Subset.objects.first()
        self.assertEqual(subset.name, 'Name')
        self.assertEqual(subset.description, 'Description')
        self.assertEqual(subset.project, project)
        self.assertEqual(subset.creator, user)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/admin/projects/%s/subsets/%s/' % (project.id, subset.id),
            response['location']
        )


class SubsetSettingsTest(TestCase):
    def setUp(self):
        self.view = SubsetSettings.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser should redirect to the login
        pages
        """
        subset = SubsetFactory.create()
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_anonymous(self):
        """
        Updating with AnonymousUser should redirect to the login page
        """
        subset = SubsetFactory.create()
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'description': 'Description',
        }
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

        reference = Subset.objects.get(pk=subset.id)
        self.assertNotEqual(reference.name, 'Name')
        self.assertNotEqual(reference.description, 'Description')

    def test_get_with_user(self):
        """
        Accessing the view with normal user should render the page with an
        error message
        """
        user = UserFactory.create()
        subset = SubsetFactory.create()

        self.request.user = user
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        rendered = render_to_string(
            'subsets/subsets_settings.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_user(self):
        """
        Updating with normal user should render the page with an error message
        """
        user = UserFactory.create()
        subset = SubsetFactory.create()

        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'description': 'Description',
        }

        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        rendered = render_to_string(
            'subsets/subsets_settings.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

        reference = Subset.objects.get(pk=subset.id)
        self.assertNotEqual(reference.name, 'Name')
        self.assertNotEqual(reference.description, 'Description')

    def test_get_with_admin(self):
        """
        Accessing the view with project admin should render the page
        """
        subset = SubsetFactory.create()
        user = subset.project.creator

        self.request.user = user
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        rendered = render_to_string(
            'subsets/subsets_settings.html',
            {
                'subset': subset,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_admin(self):
        """
        Accessing the view with project admin should render the page
        """
        subset = SubsetFactory.create()
        user = subset.project.creator

        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'description': 'Description',
        }

        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        reference = Subset.objects.get(pk=subset.id)
        self.assertEqual(reference.name, 'Name')
        self.assertEqual(reference.description, 'Description')

        rendered = render_to_string(
            'subsets/subsets_settings.html',
            {
                'subset': reference,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_non_existing_with_admin(self):
        """
        Accessing the view with project admin should render an error message
        """
        project = ProjectFactory.create()
        user = project.creator

        self.request.user = user
        response = self.view(
            self.request,
            project_id=project.id,
            subset_id=634842156456).render()

        rendered = render_to_string(
            'subsets/subsets_settings.html',
            {
                'error_description': 'Subset matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_non_existing_with_admin(self):
        """
        Update the view with project admin should render an error message
        """
        project = ProjectFactory.create()
        user = project.creator

        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'description': 'Description',
        }

        response = self.view(
            self.request,
            project_id=project.id,
            subset_id=634842156456).render()

        rendered = render_to_string(
            'subsets/subsets_settings.html',
            {
                'error_description': 'Subset matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


class SubsetDataTest(TestCase):
    def setUp(self):
        self.view = SubsetData.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Posting with AnonymousUser should redirect to the login pages and not
        update the filters
        """
        subset = SubsetFactory.create()
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_anonymous(self):
        """
        Accessing the view with AnonymousUser should redirect to the login
        pages
        """
        subset = SubsetFactory.create()
        category = CategoryFactory.create(**{'project': subset.project})

        self.request.method = 'POST'
        self.request.POST = {
            'filters': '{ "%s": { } }' % category.id
        }

        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id)

        reference_subset = Subset.objects.get(pk=subset.id)
        self.assertIsNone(reference_subset.filters)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Accessing the view with normal user should render the page with an
        error message
        """
        subset = SubsetFactory.create()
        user = UserFactory.create()

        self.request.user = user
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        rendered = render_to_string(
            'subsets/subsets_data.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_user(self):
        """
        Posting with normal user should render with an error message and not
        update the filter
        """
        subset = SubsetFactory.create()
        user = UserFactory.create()

        category = CategoryFactory.create(**{'project': subset.project})

        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = {
            'filters': '{ "%s": { } }' % category.id
        }
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        reference_subset = Subset.objects.get(pk=subset.id)
        self.assertIsNone(reference_subset.filters)

        rendered = render_to_string(
            'subsets/subsets_data.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_admin(self):
        """
        Accessing the view with project admin should render the page
        """
        subset = SubsetFactory.create()
        user = subset.project.creator

        self.request.user = user
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        rendered = render_to_string(
            'subsets/subsets_data.html',
            {
                'subset': subset,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_admin(self):
        """
        Posting with admin should update the filters of the subset
        """
        subset = SubsetFactory.create()
        user = subset.project.creator

        category = CategoryFactory.create(**{'project': subset.project})

        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = {
            'filters': '{ "%s": { } }' % category.id
        }
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        reference_subset = Subset.objects.get(pk=subset.id)
        self.assertEqual(
            reference_subset.filters,
            json.loads('{ "%s": { } }' % category.id)
        )

        rendered = render_to_string(
            'subsets/subsets_data.html',
            {
                'subset': reference_subset,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'messages': get_messages(self.request),
                'GEOKEY_VERSION': version.get_version()
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


class SubsetDeleteTest(TestCase):
    def setUp(self):
        self.view = SubsetDelete.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser should redirect to the login
        pages
        """
        subset = SubsetFactory.create()
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(Subset.objects.count(), 1)

    def test_get_with_user(self):
        """
        Accessing the view with normal user should render the page with an
        error message
        """
        subset = SubsetFactory.create()
        user = UserFactory.create()

        self.request.user = user
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id).render()

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        self.assertEqual(Subset.objects.count(), 1)

    def test_get_with_admin(self):
        """
        Deleting with project admin should redirect to project list
        """
        subset = SubsetFactory.create()
        user = subset.project.creator

        self.request.user = user
        response = self.view(
            self.request,
            project_id=subset.project.id,
            subset_id=subset.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse('admin:subset_list', args=(subset.project.id, )),
            response['location']
        )
        self.assertEqual(Subset.objects.count(), 0)
