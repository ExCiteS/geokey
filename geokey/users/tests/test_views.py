"""Tests for views of users."""

import json

from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse, resolve
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.db import IntegrityError
from django.core import mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage

from nose.tools import raises

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from allauth.account.models import EmailAddress

from geokey import version
from geokey.core.tests.helpers import render_helpers
from geokey.applications.tests.model_factories import ApplicationFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory

from .model_factories import UserFactory, UserGroupFactory
from ..views import (
    UserGroup, UserGroupUsers,
    UserGroupCreate, UserGroupSettings, UserProfile,
    CreateUserMixin, UserAPIView, Dashboard, ChangePasswordView, Index,
    UserGroupList, UserGroupOverview, AdministratorsOverview,
    UserGroupPermissions, UserGroupDelete, UserGroupData
)
from ..models import User, UserGroup as Group


# ############################################################################
#
# ADMIN VIEWS
#
# ############################################################################

class IndexTest(TestCase):

    def get(self, user):
        factory = RequestFactory()
        view = Index.as_view()
        url = reverse('admin:index')
        request = factory.get(url)
        request.user = user
        return view(request)

    def test_with_user(self):
        request = self.get(UserFactory.create())
        self.assertEqual(request.status_code, 302)

    def test_with_anonymous(self):
        request = self.get(AnonymousUser())
        self.assertEqual(request.status_code, 200)


class DashboardTest(TestCase):
    """Test dashboard page."""

    def setUp(self):
        """Set up tests."""
        self.creator = UserFactory.create()
        self.admin = UserFactory.create()
        self.view_member = UserFactory.create()
        self.contributor = UserFactory.create()
        ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        ProjectFactory.create(
            add_admins=[self.admin, self.contributor]
        )

    def test_get_context_data_with_admin(self):
        """Test GET with admin."""
        dashboard_view = Dashboard()
        url = reverse('admin:dashboard')
        request = APIRequestFactory().get(url)

        request.user = self.admin
        dashboard_view.request = request
        context = dashboard_view.get_context_data()

        self.assertEqual(len(context.get('projects')), 2)

    def test_get_context_data_with_contributor(self):
        """Test GET with contributor."""
        dashboard_view = Dashboard()
        url = reverse('admin:dashboard')
        request = APIRequestFactory().get(url)

        request.user = self.contributor
        dashboard_view.request = request
        context = dashboard_view.get_context_data()

        self.assertEqual(len(context.get('projects')), 1)


class UserGroupListTest(TestCase):

    def test(self):
        project = ProjectFactory.create()
        UserGroupFactory.create_batch(3, **{'project': project})

        view = UserGroupList()
        url = reverse(
            'admin:usergroup_list', kwargs={'project_id': project.id}
        )
        request = APIRequestFactory().get(url, project_id=project.id)

        request.user = project.creator
        view.request = request
        context = view.get_context_data(project.id)

        self.assertEqual(context.get('project'), project)


class CreateUserMixinTest(TransactionTestCase):

    def setUp(self):
        self.data = {
            'display_name': 'user-1',
            'email': 'user-1@example.com',
            'password': '123'
        }

    def tearDown(self):
        User.objects.all().delete()

    def test_create_user(self):
        create_mixin = CreateUserMixin()
        user = create_mixin.create_user(self.data)

        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.display_name, self.data.get('display_name'))
        self.assertEqual(user.email, self.data.get('email'))

    @raises(IntegrityError)
    def test_create_user_with_taken_email(self):
        create_mixin = CreateUserMixin()
        UserFactory.create(**{'email': 'user-1@example.com'})

        user = create_mixin.create_user(self.data)
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.display_name, self.data.get('username'))
        self.assertEqual(user.email, self.data.get('email'))


class UserGroupCreateTest(TestCase):

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
        view = UserGroupCreate.as_view()
        url = reverse('admin:usergroup_create', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(request, project_id=self.project.id).render()

    def post(self, user):
        data = {
            'name': 'Name',
            'description': 'Description',
            'can_contribute': True,
            'can_moderate': True
        }
        view = UserGroupCreate.as_view()
        url = reverse('admin:usergroup_create', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.post(url, data)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

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
            'Project matching query does not exist'
        )

    def test_post_with_admin(self):
        response = self.post(self.admin)
        self.assertEqual(response.status_code, 302)

    def test_post_with_admin_on_locked_project(self):
        self.project.islocked = True
        self.project.save()

        response = self.post(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'The project is locked. New user groups cannot be created.'
        )

    def test_post_with_contributor(self):
        response = self.post(self.contributor).render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_post_with_anonymous(self):
        response = self.post(self.non_member).render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist'
        )


class UserGroupOverviewTest(TestCase):

    def test(self):
        project = ProjectFactory.create()
        usergroup = UserGroupFactory.create(**{'project': project})

        view = UserGroupOverview()
        url = reverse(
            'admin:usergroup_overview',
            kwargs={'project_id': project.id, 'usergroup_id': usergroup.id}
        )
        request = APIRequestFactory().get(
            url, project_id=project.id, usergroup_id=usergroup.id)

        request.user = project.creator
        view.request = request
        context = view.get_context_data(project.id, usergroup.id)

        self.assertEqual(context.get('usergroup'), usergroup)


class AdministratorsOverviewTest(TestCase):

    def test(self):
        project = ProjectFactory.create()

        view = AdministratorsOverview()
        url = reverse(
            'admin:admins_overview',
            kwargs={'project_id': project.id}
        )
        request = APIRequestFactory().get(
            url, project_id=project.id)

        request.user = project.creator
        view.request = request
        context = view.get_context_data(project.id)

        self.assertEqual(context.get('project'), project)


class UserGroupSettingTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.usergroup = UserGroupFactory(**{'project': self.project})

    def get(self, user):
        view = UserGroupSettings.as_view()
        url = reverse('admin:usergroup_settings', kwargs={
            'project_id': self.project.id,
            'usergroup_id': self.usergroup.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            usergroup_id=self.usergroup.id).render()

    def post(self, user):
        self.data = {
            'name': 'New name',
            'description': 'Description'
        }
        view = UserGroupSettings.as_view()
        url = reverse('admin:usergroup_settings', kwargs={
            'project_id': self.project.id,
            'usergroup_id': self.usergroup.id
        })
        request = self.factory.post(url, self.data)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            usergroup_id=self.usergroup.id).render()

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
            'Project matching query does not exist'
        )

    def test_post_settings_with_admin(self):
        response = self.post(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Group.objects.get(pk=self.usergroup.id)
        self.assertEqual(self.data.get('name'), ref.name)
        self.assertEqual(self.data.get('description'), ref.description)

    def test_post_settings_with_contributor(self):
        response = self.post(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

        ref = Group.objects.get(pk=self.usergroup.id)
        self.assertNotEqual(self.data.get('name'), ref.name)
        self.assertNotEqual(self.data.get('description'), ref.description)

    def test_post_settings_with_non_member(self):
        response = self.post(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist'
        )

        ref = Group.objects.get(pk=self.usergroup.id)
        self.assertNotEqual(self.data.get('name'), ref.name)
        self.assertNotEqual(self.data.get('description'), ref.description)


class UserGroupPermissionsTest(TestCase):

    def test(self):
        project = ProjectFactory.create()
        usergroup = UserGroupFactory.create(**{'project': project})

        view = UserGroupPermissions()
        url = reverse(
            'admin:usergroup_permissions',
            kwargs={'project_id': project.id, 'usergroup_id': usergroup.id}
        )
        request = APIRequestFactory().get(
            url, project_id=project.id, usergroup_id=usergroup.id)

        request.user = project.creator
        view.request = request
        context = view.get_context_data(project.id, usergroup.id)

        self.assertEqual(context.get('usergroup'), usergroup)


class UserGroupDataTest(TestCase):

    def test_url(self):
        self.assertEqual(
            reverse(
                'admin:usergroup_data',
                kwargs={'project_id': 1, 'usergroup_id': 1}
            ),
            '/admin/projects/1/usergroups/1/data/'
        )

        resolved = resolve('/admin/projects/1/usergroups/1/data/')
        self.assertEqual(resolved.kwargs['project_id'], '1')
        self.assertEqual(resolved.kwargs['usergroup_id'], '1')
        self.assertEqual(resolved.func.func_name, UserGroupData.__name__)

    def test_views_with_admin(self):
        usergroup = UserGroupFactory.create()
        view = UserGroupData.as_view()

        request = HttpRequest()
        request.method = 'GET'
        request.user = usergroup.project.creator

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=usergroup.project.id,
            usergroup_id=usergroup.id
        ).render()
        response = render_helpers.remove_csrf(unicode(response.content))

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'project': usergroup.project,
                'usergroup': usergroup,
                'user': usergroup.project.creator,
                'messages': get_messages(request),
                'PLATFORM_NAME': get_current_site(request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response, rendered)

        request = HttpRequest()
        request.method = 'POST'
        request.user = usergroup.project.creator
        request.POST = {'permission': 'all', 'filters': ''}

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=usergroup.project.id,
            usergroup_id=usergroup.id
        ).render()
        response = render_helpers.remove_csrf(unicode(response.content))

        ref = Group.objects.get(pk=usergroup.id)

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'project': ref.project,
                'usergroup': ref,
                'user': ref.project.creator,
                'messages': get_messages(request),
                'PLATFORM_NAME': get_current_site(request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response, rendered)
        self.assertIsNone(ref.filters)

        category = CategoryFactory.create(**{'project': usergroup.project})
        request = HttpRequest()
        request.method = 'POST'
        request.user = usergroup.project.creator
        request.POST = {
            'permission': 'restricted',
            'filters': '{ "%s": { } }' % category.id
        }

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=usergroup.project.id,
            usergroup_id=usergroup.id
        ).render()
        response = render_helpers.remove_csrf(unicode(response.content))

        ref = Group.objects.get(pk=usergroup.id)

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'project': ref.project,
                'usergroup': ref,
                'user': ref.project.creator,
                'messages': get_messages(request),
                'PLATFORM_NAME': get_current_site(request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response, rendered)
        self.assertEqual(
            ref.filters,
            json.loads('{ "%s": { } }' % category.id)
        )

    def test_post_with_admin_on_locked_project(self):
        usergroup = UserGroupFactory.create()
        view = UserGroupData.as_view()

        usergroup.project.islocked = True
        usergroup.project.save()

        category = CategoryFactory.create(**{'project': usergroup.project})
        request = HttpRequest()
        request.method = 'POST'
        request.user = usergroup.project.creator
        request.POST = {
            'permission': 'restricted',
            'filters': '{ "%s": { } }' % category.id
        }

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=usergroup.project.id,
            usergroup_id=usergroup.id
        ).render()
        response = render_helpers.remove_csrf(unicode(response.content))

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'project': usergroup.project,
                'usergroup': usergroup,
                'user': usergroup.project.creator,
                'messages': get_messages(request),
                'PLATFORM_NAME': get_current_site(request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response, rendered)
        self.assertIsNone(Group.objects.get(pk=usergroup.id).filters)

    def test_views_with_other_user(self):
        user = UserFactory.create()
        usergroup = UserGroupFactory.create()
        view = UserGroupData.as_view()

        request = HttpRequest()
        request.method = 'GET'
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=usergroup.project.id,
            usergroup_id=usergroup.id
        ).render()
        response = render_helpers.remove_csrf(unicode(response.content))

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'messages': get_messages(request),
                'PLATFORM_NAME': get_current_site(request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response, rendered)

        category = CategoryFactory.create(**{'project': usergroup.project})
        request = HttpRequest()
        request.method = 'POST'
        request.user = user
        request.POST = {
            'permission': 'restricted',
            'filters': '{ "%s": { } }' % category.id
        }

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=usergroup.project.id,
            usergroup_id=usergroup.id
        ).render()
        response = render_helpers.remove_csrf(unicode(response.content))

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'messages': get_messages(request),
                'PLATFORM_NAME': get_current_site(request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response, rendered)
        self.assertIsNone(Group.objects.get(pk=usergroup.id).filters)


class UserGroupDeleteTest(TestCase):

    def setUp(self):
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.usergroup = UserGroupFactory.create(**{'project': self.project})

    def test_delete_with_admin(self):
        view = UserGroupDelete.as_view()
        url = reverse(
            'admin:usergroup_delete',
            kwargs={
                'project_id': self.project.id,
                'usergroup_id': self.usergroup.id
            }
        )
        request = APIRequestFactory().get(
            url, project_id=self.project.id, usergroup_id=self.usergroup.id)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.usergroup.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 1)

    def test_delete_on_locked_project(self):
        self.project.islocked = True
        self.project.save()

        view = UserGroupDelete.as_view()
        url = reverse(
            'admin:usergroup_delete',
            kwargs={
                'project_id': self.project.id,
                'usergroup_id': self.usergroup.id
            }
        )
        request = APIRequestFactory().get(
            url, project_id=self.project.id, usergroup_id=self.usergroup.id)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.usergroup.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 2)

    def test_delete_with_contributor(self):
        view = UserGroupDelete.as_view()
        url = reverse(
            'admin:usergroup_delete',
            kwargs={
                'project_id': self.project.id,
                'usergroup_id': self.usergroup.id
            }
        )
        request = APIRequestFactory().get(
            url, project_id=self.project.id, usergroup_id=self.usergroup.id)
        request.user = self.contributor

        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.usergroup.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Group.objects.count(), 2)

    def test_delete_with_non_member(self):
        view = UserGroupDelete.as_view()
        url = reverse(
            'admin:usergroup_delete',
            kwargs={
                'project_id': self.project.id,
                'usergroup_id': self.usergroup.id
            }
        )
        request = APIRequestFactory().get(
            url, project_id=self.project.id, usergroup_id=self.usergroup.id)
        request.user = self.contributor

        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.usergroup.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Group.objects.count(), 2)


class UserProfileTest(TestCase):

    def setUp(self):
        self.view = UserProfile.as_view()
        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = 'test-server'
        self.request.META['SERVER_PORT'] = '80'

        setattr(self.request, 'session', 'session')
        _messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', _messages)

    def test_get_with_anonymous_user(self):
        """
        Accessing the view with anonymous user should redirect to the login
        page.
        """
        self.request.method = 'GET'
        self.request.user = AnonymousUser()
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_regular_user(self):
        """
        Accessing the view with regular user should render the page.
        """
        self.request.method = 'GET'
        self.request.user = UserFactory.create()
        response = self.view(self.request).render()

        rendered = render_to_string(
            'users/profile.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user
            }
        )
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

    def test_post_with_anonymous_user(self):
        """
        Updating user profile with anonymous user should redirect to the login
        page.
        """
        self.request.method = 'POST'
        self.request.user = AnonymousUser()
        self.request.POST = {
            'display_name': 'Test User',
            'email': 'test-user@example.com'
        }
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_regular_user(self):
        """
        Updating user profile with regular user should change the information
        and show success message.
        """
        self.request.method = 'POST'
        self.request.user = UserFactory.create()
        self.request.POST = {
            'display_name': 'Test User',
            'email': 'test-user@example.com'
        }
        EmailAddress.objects.create(
            user=self.request.user,
            email=self.request.user.email,
            verified=True
        )
        response = self.view(self.request).render()

        rendered = render_to_string(
            'users/profile.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

        reference = User.objects.get(pk=self.request.user.id)
        self.assertEqual(
            reference.display_name,
            self.request.POST.get('display_name')
        )
        self.assertEqual(
            reference.email,
            self.request.POST.get('email')
        )

        reference = EmailAddress.objects.get(user=self.request.user)
        self.assertEqual(
            reference.email,
            self.request.POST.get('email')
        )
        self.assertEqual(reference.verified, False)

    def test_post_with_regular_user_when_information_has_not_changed(self):
        """
        Updating user profile with regular user should not change the
        information if it has not been changed. It should also show info
        message.
        """
        self.request.method = 'POST'
        self.request.user = UserFactory.create()
        self.request.POST = {
            'display_name': self.request.user.display_name,
            'email': self.request.user.email
        }
        EmailAddress.objects.create(
            user=self.request.user,
            email=self.request.user.email,
            verified=True
        )
        response = self.view(self.request).render()

        rendered = render_to_string(
            'users/profile.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

        reference = EmailAddress.objects.get(user=self.request.user)
        self.assertEqual(reference.verified, True)

    def test_post_with_regular_user_when_email_has_not_changed(self):
        """
        Updating user profile with regular user should change the display name,
        but not update the email if it has not been changed. It should also
        show success message.
        """
        self.request.method = 'POST'
        self.request.user = UserFactory.create()
        self.request.POST = {
            'display_name': 'Test User',
            'email': self.request.user.email,
        }
        EmailAddress.objects.create(
            user=self.request.user,
            email=self.request.user.email,
            verified=True
        )
        response = self.view(self.request).render()

        rendered = render_to_string(
            'users/profile.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

        reference = User.objects.get(pk=self.request.user.id)
        self.assertEqual(
            reference.display_name,
            self.request.POST.get('display_name')
        )

        reference = EmailAddress.objects.get(user=self.request.user)
        self.assertEqual(reference.verified, True)

    def test_post_with_regular_user_when_email_address_object_not_found(self):
        """
        Updating user profile with regular user should create EmailAddress
        object, if it does not exist.
        """
        self.request.method = 'POST'
        self.request.user = UserFactory.create()
        self.request.POST = {
            'display_name': 'Test User',
            'email': 'test-user@example.com'
        }
        response = self.view(self.request).render()

        rendered = render_to_string(
            'users/profile.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

        self.assertEqual(
            EmailAddress.objects.filter(user=self.request.user).exists(),
            True
        )
        reference = EmailAddress.objects.get(user=self.request.user)
        self.assertEqual(
            reference.email,
            self.request.POST.get('email')
        )
        self.assertEqual(reference.verified, False)

        rendered = render_to_string(
            'users/profile.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

        reference = User.objects.get(pk=self.request.user.id)
        self.assertEqual(
            reference.display_name,
            self.request.POST.get('display_name')
        )
        self.assertEqual(
            reference.email,
            self.request.POST.get('email')
        )

        reference = EmailAddress.objects.get(user=self.request.user)
        self.assertEqual(
            reference.email,
            self.request.POST.get('email')
        )
        self.assertEqual(reference.verified, False)


# ############################################################################
#
# AJAX VIEWS
#
# ############################################################################

class QueryUsersTest(TestCase):

    def _get(self, query):
        return self.client.get('/ajax/users/?query=' + query)

    def setUp(self):
        UserFactory.create(**{
            'display_name': 'Peter Schmeichel'
        })
        UserFactory.create(**{
            'display_name': 'George Best'
        })
        UserFactory.create(**{
            'display_name': 'Luis Figo'
        })
        UserFactory.create(**{
            'display_name': 'pete23'
        })
        UserFactory.create(**{
            'display_name': 'pet48'
        })
        UserFactory.create(**{
            'display_name': 'Frank Lampard'
        })

    def test_query_pet(self):
        response = self._get('pet')

        result_set = json.loads(response.content)
        self.assertEqual(len(result_set), 3)
        self.assertContains(response, 'Schmeichel')
        self.assertContains(response, 'pete23')
        self.assertContains(response, 'pet48')

    def test_query_peter(self):
        response = self._get('peter')
        result_set = json.loads(response.content)
        self.assertEqual(len(result_set), 1)
        self.assertContains(response, 'Schmeichel')

    def test_query_anonymous(self):
        response = self._get('anon')
        result_set = json.loads(response.content)
        self.assertEqual(len(result_set), 0)

    def test_no_query(self):
        response = self.client.get('/ajax/users/')
        result_set = json.loads(response.content)
        self.assertEqual(len(result_set), 0)


class UserGroupTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()
        self.user_to_add = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin]
        )

        self.contributors = UserGroupFactory(
            add_users=[self.contributor],
            **{'project': self.project}
        )

    def put(self, user, data):
        url = reverse('ajax:usergroup', kwargs={
            'project_id': self.project.id,
            'usergroup_id': self.contributors.id
        })
        request = self.factory.put(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = UserGroup.as_view()

        return view(
            request,
            project_id=self.project.id,
            usergroup_id=self.contributors.id).render()

    def test_update_with_admin(self):
        response = self.put(self.admin, {'can_contribute': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Group.objects.get(pk=self.contributors.id).can_contribute,
        )

    def test_when_project_is_locked(self):
        self.project.islocked = True
        self.project.save()

        response = self.put(self.admin, {'can_contribute': False})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            Group.objects.get(pk=self.contributors.id).can_contribute,
        )

    def test_invalid_update_with_admin(self):
        response = self.put(self.admin, {'can_contribute': 'Blah'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            Group.objects.get(pk=self.contributors.id).can_contribute,
        )

    def test_update_description_with_contributor(self):
        response = self.put(self.contributor, {'can_contribute': False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Group.objects.get(pk=self.contributors.id).can_contribute,
        )

    def test_update_description_with_non_member(self):
        response = self.put(self.non_member, {'can_contribute': False})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Group.objects.get(pk=self.contributors.id).can_contribute,
        )


class UserGroupUsersTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()
        self.user_to_add = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin]
        )

        self.contributors = UserGroupFactory(
            add_users=[self.contributor],
            **{'project': self.project}
        )

    def test_add_to_not_existing_usergroup(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, 6545454844545648),
            {'user_id': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=6545454844545648
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_add_not_existing_user(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, self.contributors.id),
            {'user_id': 4445468756454}
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.contributors.id
        ).render()

        self.assertEqual(response.status_code, 400)

    def test_add_on_locked_project(self):
        self.project.islocked = True
        self.project.save()

        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, self.contributors.id),
            {'user_id': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.contributors.id
        ).render()

        self.assertEqual(response.status_code, 400)

    def test_add_contributor_with_admin(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, self.contributors.id),
            {'user_id': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.contributors.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            self.user_to_add,
            self.contributors.users.all()
        )

    def test_add_contributor_with_contributor(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, self.contributors.id),
            {'user_id': self.user_to_add.id}
        )
        force_authenticate(request, user=self.contributor)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.contributors.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            self.contributors.users.all()
        )

    def test_add_contributor_with_non_member(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, self.contributors.id),
            {'user_id': self.user_to_add.id}
        )
        force_authenticate(request, user=self.non_member)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.contributors.id
        ).render()

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(
            self.user_to_add,
            self.contributors.users.all()
        )


class ChangePasswordTest(TestCase):

    def test_changepassword(self):
        user = UserFactory.create(**{'password': '123456'})
        factory = APIRequestFactory()
        url = reverse('api:changepassword')
        data = {
            'oldpassword': '123456',
            'password1': '1234567',
            'password2': '1234567',
        }
        request = factory.post(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = ChangePasswordView.as_view()
        response = view(request).render()
        self.assertEqual(response.status_code, 204)

    def test_changepassword_with_anonymous(self):
        factory = APIRequestFactory()
        url = reverse('api:changepassword')
        data = {
            'oldpassword': '123456',
            'password1': '1234567',
            'password2': '1234567',
        }
        request = factory.post(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=AnonymousUser())
        view = ChangePasswordView.as_view()
        response = view(request).render()
        self.assertEqual(response.status_code, 401)

    def test_changepassword_wrong_oldpassword(self):
        user = UserFactory.create(**{'password': '123456'})
        factory = APIRequestFactory()
        url = reverse('api:changepassword')
        data = {
            'oldpassword': '12345',
            'password1': '1234567',
            'password2': '1234567',
        }
        request = factory.post(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = ChangePasswordView.as_view()
        response = view(request).render()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content).get('errors').get('oldpassword')[0],
            'Please type your current password.'
        )

    def test_changepassword_password_dont_match(self):
        user = UserFactory.create(**{'password': '123456'})
        factory = APIRequestFactory()
        url = reverse('api:changepassword')
        data = {
            'oldpassword': '123456',
            'password1': '12345687',
            'password2': '12345678',
        }
        request = factory.post(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = ChangePasswordView.as_view()
        response = view(request).render()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content).get('errors').get('password2')[0],
            'You must type the same password each time.'
        )


class UserAPIViewTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = reverse('api:user_api')
        self.client = ApplicationFactory.create()
        self.user_data = {
            'display_name': 'user 1',
            'email': 'user-1@example.com',
            'password1': '123456',
            'password2': '123456'
        }
        self.data = self.user_data.copy()
        self.data['client_id'] = self.client.client_id

    def test_get_user(self):
        user = UserFactory.create()
        view = UserAPIView.as_view()
        request = self.factory.get(self.url)
        request.user = user
        response = view(request).render()

        self.assertEqual(response.status_code, 200)

        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        response = view(request).render()

        self.assertEqual(response.status_code, 401)

    def test_update_user(self):
        user = UserFactory.create()
        EmailAddress.objects.create(user=user, email=user.email)

        view = UserAPIView.as_view()
        data = {
            'display_name': 'user-1',
            'email': 'user-1@example.com'
        }

        request = self.factory.patch(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        request.user = AnonymousUser()
        response = view(request).render()
        self.assertEqual(response.status_code, 401)

        request = self.factory.patch(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        request.user = user
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_update_user_display_name(self):
        user = UserFactory.create()
        EmailAddress.objects.create(user=user, email=user.email)

        view = UserAPIView.as_view()
        data = {
            'display_name': 'user-2'
        }

        request = self.factory.patch(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        request.user = AnonymousUser()
        response = view(request).render()
        self.assertEqual(response.status_code, 401)

        request = self.factory.patch(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        request.user = user
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_update_user_display_name_with_whitespace(self):
        user = UserFactory.create()
        EmailAddress.objects.create(user=user, email=user.email)

        view = UserAPIView.as_view()
        data = {
            'display_name': 'user-2 sdfdf'
        }

        request = self.factory.patch(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        request.user = AnonymousUser()
        response = view(request).render()
        self.assertEqual(response.status_code, 401)

        request = self.factory.patch(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        request.user = user
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_update_old_user_email(self):
        user = UserFactory.create()

        view = UserAPIView.as_view()
        data = {
            'display_name': 'user-2',
            'email': 'user-215@example.com'
        }

        request = self.factory.patch(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        request.user = user
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_update_user_existing(self):
        data = {
            'display_name': 'user-1',
            'email': 'user-1@example.com'
        }
        UserFactory.create(**data)
        user = UserFactory.create()
        view = UserAPIView.as_view()

        request = self.factory.patch(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        request.user = user
        response = view(request).render()
        self.assertEqual(response.status_code, 400)

    def test_sign_up(self):
        request = self.factory.post(
            self.url, json.dumps(self.data), content_type='application/json')

        view = UserAPIView.as_view()
        response = view(request).render()
        self.assertEqual(response.status_code, 201)

        user_json = json.loads(response.content)
        self.assertEqual(
            user_json.get('display_name'),
            self.data.get('display_name')
        )
        self.assertEquals(len(mail.outbox), 1)

    def test_sign_with_existing_email(self):
        UserFactory.create(**{
            'display_name': 'USer-3',
            'email': 'user-1@example.com'}
        )

        data = {
            'client_id': self.client.client_id,
            'username': 'user-3',
            'email': 'user-3@example.com',
            'password1': '123456',
            'password2': '123456'
        }

        request = self.factory.post(
            self.url, json.dumps(data), content_type='application/json')
        view = UserAPIView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.content)
        self.assertEqual(len(errors.get('errors')), 1)

    def test_sign_with_empty_display(self):
        data = {
            'client_id': self.client.client_id,
            'email': 'user-1@example.com',
            'password1': '123456',
            'password2': '123456'
        }

        request = self.factory.post(
            self.url, json.dumps(data), content_type='application/json')
        view = UserAPIView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.content)

        self.assertEqual(len(errors.get('errors')), 1)

    def test_sign_with_existing_email_and_name(self):
        UserFactory.create(**{
            'display_name': 'user 1',
            'email': 'user-1@example.com'
        })

        request = self.factory.post(
            self.url, json.dumps(self.data), content_type='application/json')
        view = UserAPIView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.content)
        self.assertEqual(len(errors.get('errors')), 2)

    def test_without_client_id(self):
        request = self.factory.post(
            self.url,
            json.dumps(self.user_data),
            content_type='application/json'
        )
        view = UserAPIView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)
