"""Tests for admin views of users."""

import json
from datetime import datetime, timedelta

from django.contrib.auth import hashers
from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse, resolve
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponseRedirect
from django.db import IntegrityError
from django.core import mail
from django.template.loader import render_to_string
from django.test.utils import override_settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages import get_messages, WARNING
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone

from nose.tools import raises
from oauth2_provider.models import AccessToken

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialApp, SocialAccount

from geokey import version
from geokey.core.tests.helpers import render_helpers
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory

from .model_factories import UserFactory, UserGroupFactory, ApplicationFactory
from ..views import (
    UserGroupCreate, UserGroupSettings, UserProfile, AccountDisconnect,
    CreateUserMixin, UserAPIView, Dashboard, ChangePasswordView, Index,
    UserGroupList, UserGroupOverview, AdministratorsOverview,
    UserGroupPermissions, UserGroupDelete, UserGroupData, DeleteUser
)
from ..models import User, UserGroup as Group


class IndexTest(TestCase):

    @staticmethod
    def get(user):
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
        self.assertEqual(resolved.func.__name__, UserGroupData.__name__)

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
        response = render_helpers.remove_csrf(str(response.content.decode()))

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
        response = render_helpers.remove_csrf(response.content.decode())

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
        response = render_helpers.remove_csrf(response.content.decode())

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
        response = render_helpers.remove_csrf(str(response.content.decode()))

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
        response = render_helpers.remove_csrf(str(response.content.decode()))

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
        response = render_helpers.remove_csrf(response.content.decode())

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
                'user': self.request.user,
                'accounts': SocialAccount.objects.filter(
                    user=self.request.user)
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
                'accounts': SocialAccount.objects.filter(
                    user=self.request.user),
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
                'accounts': SocialAccount.objects.filter(
                    user=self.request.user),
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
                'accounts': SocialAccount.objects.filter(
                    user=self.request.user),
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
                'accounts': SocialAccount.objects.filter(
                    user=self.request.user),
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
                'accounts': SocialAccount.objects.filter(
                    user=self.request.user),
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


class AccountDisconnectTest(TestCase):

    def setUp(self):
        self.view = AccountDisconnect.as_view()

        self.social_app = SocialApp.objects.create(
            provider='facebook',
            name='Facebook',
            client_id='xxxxxxxxxxxxxxxxxx',
            secret='xxxxxxxxxxxxxxxxxx',
            key='')

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_EMAIL_VERIFICATION='none')
    def test_get_with_anonymous(self):
        user = UserFactory.create(password='myPassword2016')

        social_account = SocialAccount.objects.create(
            user=user,
            provider='facebook')

        url = reverse(
            'admin:account_disconnect',
            kwargs={'account_id': social_account.id})
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        self.social_app.sites.add(get_current_site(request))

        response = self.view(request, account_id=social_account.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(SocialAccount.objects.count(), 1)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_EMAIL_VERIFICATION='none')
    def test_get_with_user(self):
        hashed_password = hashers.make_password(password='myPassword2016')
        user = UserFactory.create(password=hashed_password, )

        social_account = SocialAccount.objects.create(
            user=user,
            provider='facebook')

        url = reverse(
            'admin:account_disconnect',
            kwargs={'account_id': social_account.id})
        request = APIRequestFactory().get(url)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        self.social_app.sites.add(get_current_site(request))

        response = self.view(request, account_id=social_account.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(SocialAccount.objects.count(), 0)

        messages = get_messages(request)
        msg = list(messages)[0]
        self.assertEqual(msg.tags, 'success')
        self.assertTrue(
            'The account has been disconnected.' in msg.message)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_EMAIL_VERIFICATION='none')
    def test_get_with_user_when_not_personal_account(self):
        user = UserFactory.create(password='myPassword2016')

        social_account = SocialAccount.objects.create(
            user=UserFactory.create(password='awesomePassword2016'),
            provider='facebook')

        url = reverse(
            'admin:account_disconnect',
            kwargs={'account_id': social_account.id})
        request = APIRequestFactory().get(url)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        self.social_app.sites.add(get_current_site(request))

        response = self.view(request, account_id=social_account.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(SocialAccount.objects.count(), 1)

        messages = get_messages(request)
        msg = list(messages)[0]
        self.assertEqual(msg.tags, 'danger')
        self.assertTrue(
            'The account could not be found.' in msg.message)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_EMAIL_VERIFICATION='none')
    def test_get_with_user_when_not_exist(self):
        user = UserFactory.create(password='myPassword2016')

        SocialAccount.objects.create(
            user=user,
            provider='facebook')

        url = reverse(
            'admin:account_disconnect',
            kwargs={'account_id': 1254548421148})
        request = APIRequestFactory().get(url)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        self.social_app.sites.add(get_current_site(request))

        response = self.view(request, account_id=1254548421148)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(SocialAccount.objects.count(), 1)

        messages = get_messages(request)
        msg = list(messages)[0]
        self.assertEqual(msg.tags, 'danger')
        self.assertTrue(
            'The account could not be found.' in msg.message)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_EMAIL_VERIFICATION='none')
    def test_get_with_user_when_no_password(self):
        user = UserFactory.create(password='')

        social_account = SocialAccount.objects.create(
            user=user,
            provider='facebook')

        url = reverse(
            'admin:account_disconnect',
            kwargs={'account_id': social_account.id})
        request = APIRequestFactory().get(url)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        self.social_app.sites.add(get_current_site(request))

        response = self.view(request, account_id=social_account.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(SocialAccount.objects.count(), 1)

        messages = get_messages(request)
        msg = list(messages)[0]
        self.assertEqual(msg.tags, 'danger')
        self.assertTrue(
            'Your account has no password set up.' in msg.message)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_EMAIL_VERIFICATION='mandatory')
    def test_get_with_user_when_email_not_verified(self):
        hashed_password = hashers.make_password(password='myPassword2016')
        user = UserFactory.create(password=hashed_password, )

        social_account = SocialAccount.objects.create(
            user=user,
            provider='facebook')

        url = reverse(
            'admin:account_disconnect',
            kwargs={'account_id': social_account.id})
        request = APIRequestFactory().get(url)
        request.user = user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        self.social_app.sites.add(get_current_site(request))

        response = self.view(request, account_id=social_account.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(SocialAccount.objects.count(), 1)

        messages = get_messages(request)
        msg = list(messages)[0]
        self.assertEqual(msg.tags, 'danger')
        self.assertTrue(
            'Your account has no verified e-mail address.' in msg.message)


class ChangePasswordTest(TestCase):

    def test_changepassword(self):
        hashed_password = hashers.make_password(password='123456')
        user = UserFactory.create(**{'password': hashed_password})
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
        self.assertEqual(len(mail.outbox), 1)

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


class UserDeleteTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        self.admin = UserFactory.create(is_superuser=True, **{'display_name': 'delete_test_admin_user'})
        self.user_no_contributions = UserFactory.create(**{'display_name': 'delete_test_no_contribs_user'})
        self.user_with_contributions = UserFactory.create(**{'display_name': 'delete_test_contribs_user',
                                                             'email': 'veryspecific@email.address.hh',
                                                             'date_joined': '2016-12-15 14:22:24.632764Z',
                                                             'last_login': '2018-01-01 10:00:00.000001Z'})
        token_expiry = timezone.now() + timedelta(hours=1)
        app = ApplicationFactory.create()
        self.access_token_contribs = AccessToken.objects.get_or_create(**{'user': self.user_with_contributions,
                                                                          'expires': token_expiry,
                                                                          'application': app,
                                                                          'scope': ''})
        # TODO: Also remove user from admins and contributors.
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.user_with_contributions],
            **{'creator': self.user_with_contributions, 'name': 'user_delete_test_project1'}
        ).save()

        self.social_post = None
        self.social_pull = None
        self.subset = None
        self.view = DeleteUser.as_view()
        self.url = reverse('admin:delete_user',)

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def tearDown(self):
        pass

    def _post(self, data, user):
        request = self.factory.post(
            self.url, json.dumps(data), content_type='application/json')
        request.user = user
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        force_authenticate(request, user=user)

        return self.view(request).render()

    def test_correct_template_response(self):
        request = APIRequestFactory().get(self.url, user_id=self.user_no_contributions.id)
        request.user = self.user_no_contributions
        response = self.view(request, user_id=self.user_no_contributions.id)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are about to delete your user account")

    def test_superuser_not_deleted(self):
        self.request.user = self.admin
        self.request.method = 'POST'
        self.request.POST = {
            'filters': '{ "%s": { } }' % self.admin.id
        }
        response = self.view(self.request).render()

        self.assertEqual(response.status_code, 200)
        messages = get_messages(self.request)
        self.assertEqual(len(messages._loaded_messages), 1)
        for message in messages:
            self.assertEqual(WARNING, message.level)
            self.assertEqual("Superuser cannot be deleted. Another superuser must first revoke superuser status.",
                             message.message)

    def test_user_details_removed(self):
        self.request.user = self.user_with_contributions
        self.request.method = 'POST'
        self.request.POST = {
            'filters': '{ "%s": { } }' % self.user_with_contributions.id
        }
        session = self.client.session
        session['_language'] = 'en'
        session.save()
        setattr(self.request, 'session', session)

        user_id = self.user_with_contributions.id
        response = self.view(self.request).render()

        self.assertEqual(response.status_code, 200)

        result_user = User.objects.get_or_create(id=user_id)[0]
        self.assertEqual(result_user.display_name[:12], 'Deleted user')
        self.assertEqual(result_user.email[-17:], 'deleteduser.email')
        self.assertEqual(result_user.date_joined.strftime('%Y-%m-%d %H:%M:%S'), '2018-04-01 11:11:11')
        self.assertAlmostEqual(datetime.strftime(result_user.last_login, '%Y-%m-%d %H:%M'),
                               datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M'))
        self.assertFalse(result_user.is_active, msg="User should no longer be active.")

        access_tokens = AccessToken.objects.filter(user=result_user)
        self.assertEqual(len(access_tokens), 0, msg="Access tokens for user should be removed.")
