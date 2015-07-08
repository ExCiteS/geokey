import json

from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse, resolve
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect, HttpRequest
from django.db import IntegrityError
from django.core import mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from nose.tools import raises

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from allauth.account.models import EmailAddress

from geokey.applications.tests.model_factories import ApplicationFactory
from geokey.projects.tests.model_factories import ProjectF
from geokey.projects.models import Admins
from geokey.categories.tests.model_factories import CategoryFactory

from .model_factories import UserF, UserGroupF
from ..views import (
    UserGroup, UserGroupUsers, UserGroupSingleUser,
    UserGroupCreate, UserGroupSettings, UserProfile,
    CreateUserMixin, UserAPIView, Dashboard, UserNotifications,
    ChangePasswordView, Index, UserGroupList, UserGroupOverview,
    AdministratorsOverview, UserGroupPermissions, UserGroupDelete,
    UserGroupData
)
from ..models import User, UserGroup as Group


# ############################################################################
#
# ADMIN VIEWS
#
# ############################################################################

class IndexTest(TestCase):
    def get(sefl, user):
        factory = RequestFactory()
        view = Index.as_view()
        url = reverse('admin:index')
        request = factory.get(url)
        request.user = user
        return view(request)

    def test_with_user(self):
        request = self.get(UserF.create())
        self.assertEqual(request.status_code, 302)

    def test_with_anonymous(self):
        request = self.get(AnonymousUser())
        self.assertEqual(request.status_code, 200)


class DashboardTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.view_member = UserF.create()
        self.contributor = UserF.create()
        ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        ProjectF.create(
            add_admins=[self.admin, self.contributor]
        )

    def test_get_context_data_with_admin(self):
        dashboard_view = Dashboard()
        url = reverse('admin:dashboard')
        request = APIRequestFactory().get(url)

        request.user = self.admin
        dashboard_view.request = request
        context = dashboard_view.get_context_data()

        self.assertEqual(len(context.get('admin_projects')), 2)
        self.assertFalse(context.get('involved_projects'))

    def test_get_context_data_with_contributor(self):
        dashboard_view = Dashboard()
        url = reverse('admin:dashboard')
        request = APIRequestFactory().get(url)

        request.user = self.contributor
        dashboard_view.request = request
        context = dashboard_view.get_context_data()

        self.assertEqual(len(context.get('admin_projects')), 1)
        self.assertTrue(context.get('involved_projects'))


class UserGroupListTest(TestCase):
    def test(self):
        project = ProjectF.create()
        UserGroupF.create_batch(3, **{'project': project})

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
        UserF.create(**{'email': 'user-1@example.com'})

        user = create_mixin.create_user(self.data)
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.display_name, self.data.get('username'))
        self.assertEqual(user.email, self.data.get('email'))


class UserGroupCreateTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
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

        from django.contrib.messages.storage.fallback import FallbackStorage
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
        project = ProjectF.create()
        group = UserGroupF.create(**{'project': project})

        view = UserGroupOverview()
        url = reverse(
            'admin:usergroup_overview',
            kwargs={'project_id': project.id, 'group_id': group.id}
        )
        request = APIRequestFactory().get(
            url, project_id=project.id, group_id=group.id)

        request.user = project.creator
        view.request = request
        context = view.get_context_data(project.id, group.id)

        self.assertEqual(context.get('group'), group)


class AdministratorsOverviewTest(TestCase):
    def test(self):
        project = ProjectF.create()

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
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.usergroup = UserGroupF(**{'project': self.project})

    def get(self, user):
        view = UserGroupSettings.as_view()
        url = reverse('admin:usergroup_settings', kwargs={
            'project_id': self.project.id,
            'group_id': self.usergroup.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            group_id=self.usergroup.id).render()

    def post(self, user):
        self.data = {
            'name': 'New name',
            'description': 'Description'
        }
        view = UserGroupSettings.as_view()
        url = reverse('admin:usergroup_settings', kwargs={
            'project_id': self.project.id,
            'group_id': self.usergroup.id
        })
        request = self.factory.post(url, self.data)
        request.user = user

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            group_id=self.usergroup.id).render()

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
        project = ProjectF.create()
        group = UserGroupF.create(**{'project': project})

        view = UserGroupPermissions()
        url = reverse(
            'admin:usergroup_permissions',
            kwargs={'project_id': project.id, 'group_id': group.id}
        )
        request = APIRequestFactory().get(
            url, project_id=project.id, group_id=group.id)

        request.user = project.creator
        view.request = request
        context = view.get_context_data(project.id, group.id)

        self.assertEqual(context.get('group'), group)


class UserGroupDataTest(TestCase):
    def test_url(self):
        self.assertEqual(
            reverse(
                'admin:usergroup_data',
                kwargs={'project_id': 1, 'group_id': 1}
            ),
            '/admin/projects/1/usergroups/1/data/'
        )

        resolved = resolve('/admin/projects/1/usergroups/1/data/')
        self.assertEqual(resolved.kwargs['project_id'], '1')
        self.assertEqual(resolved.kwargs['group_id'], '1')
        self.assertEqual(resolved.func.func_name, UserGroupData.__name__)

    def test_views_with_admin(self):
        group = UserGroupF.create()
        view = UserGroupData.as_view()

        request = HttpRequest()
        request.method = 'GET'
        request.user = group.project.creator
        response = view(
            request,
            project_id=group.project.id,
            group_id=group.id
        ).render()

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'group': group,
                'user': group.project.creator,
                'PLATFORM_NAME': get_current_site(request).name
            }
        )
        self.assertEqual(unicode(response.content), rendered)

        request = HttpRequest()
        request.method = 'POST'
        request.user = group.project.creator
        request.POST = {'permission': 'all', 'filters': ''}
        response = view(
            request,
            project_id=group.project.id,
            group_id=group.id
        ).render()

        ref = Group.objects.get(pk=group.id)

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'group': ref,
                'user': ref.project.creator,
                'PLATFORM_NAME': get_current_site(request).name
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertIsNone(ref.filters)

        category = CategoryFactory.create(**{'project': group.project})
        request = HttpRequest()
        request.method = 'POST'
        request.user = group.project.creator
        request.POST = {
            'permission': 'restricted',
            'filters': '{ "%s": { } }' % category.id
        }
        response = view(
            request,
            project_id=group.project.id,
            group_id=group.id
        ).render()

        ref = Group.objects.get(pk=group.id)

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'group': ref,
                'user': ref.project.creator,
                'PLATFORM_NAME': get_current_site(request).name
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(
            ref.filters,
            json.loads('{ "%s": { } }' % category.id)
        )

    def test_views_with_other_user(self):
        user = UserF.create()
        group = UserGroupF.create()
        view = UserGroupData.as_view()

        request = HttpRequest()
        request.method = 'GET'
        request.user = user
        response = view(
            request,
            project_id=group.project.id,
            group_id=group.id
        ).render()

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(request).name
            }
        )
        self.assertEqual(unicode(response.content), rendered)

        category = CategoryFactory.create(**{'project': group.project})
        request = HttpRequest()
        request.method = 'POST'
        request.user = user
        request.POST = {
            'permission': 'restricted',
            'filters': '{ "%s": { } }' % category.id
        }
        response = view(
            request,
            project_id=group.project.id,
            group_id=group.id
        ).render()

        rendered = render_to_string(
            'users/usergroup_data.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(request).name
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertIsNone(Group.objects.get(pk=group.id).filters)


class UserGroupDeleteTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.group = UserGroupF.create(**{'project': self.project})

    def test_delete_with_admin(self):
        view = UserGroupDelete.as_view()
        url = reverse(
            'admin:usergroup_delete',
            kwargs={'project_id': self.project.id, 'group_id': self.group.id}
        )
        request = APIRequestFactory().get(
            url, project_id=self.project.id, group_id=self.group.id)
        request.user = self.admin

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=self.project.id,
            group_id=self.group.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 1)

    def test_delete_with_contributor(self):
        view = UserGroupDelete.as_view()
        url = reverse(
            'admin:usergroup_delete',
            kwargs={'project_id': self.project.id, 'group_id': self.group.id}
        )
        request = APIRequestFactory().get(
            url, project_id=self.project.id, group_id=self.group.id)
        request.user = self.contributor

        response = view(
            request,
            project_id=self.project.id,
            group_id=self.group.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Group.objects.count(), 2)

    def test_delete_with_non_member(self):
        view = UserGroupDelete.as_view()
        url = reverse(
            'admin:usergroup_delete',
            kwargs={'project_id': self.project.id, 'group_id': self.group.id}
        )
        request = APIRequestFactory().get(
            url, project_id=self.project.id, group_id=self.group.id)
        request.user = self.contributor

        response = view(
            request,
            project_id=self.project.id,
            group_id=self.group.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Group.objects.count(), 2)


class UserProfileTest(TestCase):
    def test_with_user(self):
        user = UserF.create()
        view = UserProfile.as_view()
        url = reverse('admin:userprofile')
        request = APIRequestFactory().get(url)
        request.user = user
        response = view(request).render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_anonymous(self):
        user = AnonymousUser()
        view = UserProfile.as_view()
        url = reverse('admin:userprofile')
        request = APIRequestFactory().get(url)
        request.user = user
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_post_with_user(self):
        data = {
            'email': 'blah@example.com',
            'display_name': 'Blah Name'
        }
        user = UserF.create()

        EmailAddress.objects.create(user=user, email=user.email)

        view = UserProfile.as_view()
        url = reverse('admin:userprofile')
        request = APIRequestFactory().post(url, data)
        request.user = user

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request).render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ref = User.objects.get(pk=user.id)
        self.assertEqual(ref.email, data.get('email'))
        self.assertEqual(ref.display_name, data.get('display_name'))


class UserNotificationsTest(TestCase):
    def test_with_user(self):
        user = UserF.create()
        view = UserNotifications.as_view()
        url = reverse('admin:notifications')
        request = APIRequestFactory().get(url)
        request.user = user
        response = view(request).render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_anonymous(self):
        user = AnonymousUser()
        view = UserNotifications.as_view()
        url = reverse('admin:notifications')
        request = APIRequestFactory().get(url)
        request.user = user
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_post_with_admin(self):
        user = UserF.create()
        project_1 = ProjectF.create(**{'creator': user})
        project_2 = ProjectF.create(**{'creator': user})
        data = {
            str(project_1.id): 'on'
        }

        view = UserNotifications.as_view()
        url = reverse('admin:notifications')
        request = APIRequestFactory().post(url, data)
        request.user = user

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request).render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            Admins.objects.get(project=project_1, user=user).contact
        )
        self.assertFalse(
            Admins.objects.get(project=project_2, user=user).contact
        )


# ############################################################################
#
# AJAX VIEWS
#
# ############################################################################

class QueryUsersTest(TestCase):
    def _get(self, query):
        return self.client.get('/ajax/users/?query=' + query)

    def setUp(self):
        UserF.create(**{
            'display_name': 'Peter Schmeichel'
        })
        UserF.create(**{
            'display_name': 'George Best'
        })
        UserF.create(**{
            'display_name': 'Luis Figo'
        })
        UserF.create(**{
            'display_name': 'pete23'
        })
        UserF.create(**{
            'display_name': 'pet48'
        })
        UserF.create(**{
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


class UserGroupTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.user_to_add = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{'project': self.project}
        )

    def put(self, user, data):
        url = reverse('ajax:usergroup', kwargs={
            'project_id': self.project.id,
            'group_id': self.contributors.id
        })
        request = self.factory.put(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = UserGroup.as_view()

        return view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id).render()

    def test_update_with_admin(self):
        response = self.put(self.admin, {'can_contribute': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
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
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.user_to_add = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{'project': self.project}
        )

    def test_add_to_not_existing_usergroup(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, 6545454844545648),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=6545454844545648
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_add_not_existing_user(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, self.contributors.id),
            {'userId': 4445468756454}
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id
        ).render()

        self.assertEqual(response.status_code, 400)

    def test_add_contributor_with_admin(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, self.contributors.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id
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
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.contributor)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id
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
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.non_member)
        view = UserGroupUsers.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id
        ).render()

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(
            self.user_to_add,
            self.contributors.users.all()
        )


class UserGroupSingleUserTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.contrib_to_remove = UserF.create()

        self.project = ProjectF.create(add_admins=[
            self.admin
        ])

        self.contributors = UserGroupF(add_users=[
            self.contributor, self.contrib_to_remove
        ], **{
            'project': self.project,
            'can_contribute': True
        })

    def test_delete_not_existing_user(self):
        user = UserF.create()
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.contributors.id, user.id),
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupSingleUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id,
            user_id=user.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_from_not_existing_usergroup(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, 455646445484545, self.contrib_to_remove.id),
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupSingleUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=455646445484545,
            user_id=self.contrib_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_contributor_with_admin(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.contributors.id, self.contrib_to_remove.id),
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupSingleUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id,
            user_id=self.contrib_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertNotIn(
            self.contrib_to_remove,
            self.contributors.users.all()
        )

    def test_delete_contributor_with_contributor(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.contributors.id, self.contrib_to_remove.id)
        )
        force_authenticate(request, user=self.contributor)
        view = UserGroupSingleUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id,
            user_id=self.contrib_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.contrib_to_remove,
            self.contributors.users.all()
        )

    def test_delete_contributor_with_non_member(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.contributors.id, self.contrib_to_remove.id)
        )
        force_authenticate(request, user=self.non_member)
        view = UserGroupSingleUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id,
            user_id=self.contrib_to_remove.id
        ).render()
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            self.contrib_to_remove,
            self.contributors.users.all()
        )


class ChangePasswordTest(TestCase):
    def test_changepassword(self):
        user = UserF.create(**{'password': '123456'})
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
        user = UserF.create(**{'password': '123456'})
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
        user = UserF.create(**{'password': '123456'})
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
        user = UserF.create()
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
        user = UserF.create()
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
        user = UserF.create()
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
        user = UserF.create()
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
        user = UserF.create()

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
        UserF.create(**data)
        user = UserF.create()
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
        UserF.create(**{
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
        UserF.create(**{
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
