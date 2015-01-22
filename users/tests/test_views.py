import json

from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.db import IntegrityError

from nose.tools import raises

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from applications.tests.model_factories import ApplicationFactory
from projects.tests.model_factories import ProjectF
from projects.models import Admins
from datagroupings.tests.model_factories import GroupingFactory

from .model_factories import UserF, UserGroupF, GroupingUserGroupFactory
from ..views import (
    UserGroup, UserGroupUsers, UserGroupSingleUser, UserGroupViews,
    UserGroupSingleView, UserGroupCreate, UserGroupSettings, UserProfile,
    ChangePassword, CreateUserMixin, SignupAPIView, Dashboard,
    UserNotifications
)
from ..models import User, UserGroup as Group


# ############################################################################
#
# ADMIN VIEWS
#
# ############################################################################

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
        self.assertEqual(len(context.get('involved_projects')), 0)

    def test_get_context_data_with_contributor(self):
        dashboard_view = Dashboard()
        url = reverse('admin:dashboard')
        request = APIRequestFactory().get(url)

        request.user = self.contributor
        dashboard_view.request = request
        context = dashboard_view.get_context_data()

        self.assertEqual(len(context.get('admin_projects')), 1)
        self.assertEqual(len(context.get('involved_projects')), 1)


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
        self.assertEqual(user.display_name, self.data.get('display_name'))
        self.assertEqual(user.email, self.data.get('email'))


class SignupAPIViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = reverse('sign_up_api')
        self.client = ApplicationFactory.create()
        self.user_data = {
            'display_name': 'user-1',
            'email': 'user-1@example.com',
            'password': '123'
        }
        self.data = self.user_data.copy()
        self.data['client_id'] = self.client.client_id

    def test_sign_up(self):
        request = self.factory.post(
            self.url, json.dumps(self.data), content_type='application/json')
        view = SignupAPIView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 201)

        user_json = json.loads(response.content)
        self.assertEqual(
            user_json.get('display_name'),
            self.data.get('display_name')
        )

    def test_sign_with_existing_email(self):
        UserF.create(**{
            'display_name': 'USer-3',
            'email': 'user-1@example.com'}
        )

        data = {
            'client_id': self.client.client_id,
            'display_name': 'user-3',
            'email': 'user-3@example.com',
            'password': '123'
        }

        request = self.factory.post(
            self.url, json.dumps(data), content_type='application/json')
        view = SignupAPIView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.content)
        self.assertEqual(len(errors.get('errors')), 1)

    def test_sign_with_empty_display(self):
        data = {
            'client_id': self.client.client_id,
            'email': 'user-1@example.com',
            'password': '123'
        }

        request = self.factory.post(
            self.url, json.dumps(data), content_type='application/json')
        view = SignupAPIView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.content)
        self.assertEqual(len(errors.get('errors')), 1)

    def test_sign_with_existing_email_and_name(self):
        UserF.create(**self.user_data)

        request = self.factory.post(
            self.url, json.dumps(self.data), content_type='application/json')
        view = SignupAPIView.as_view()
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
        view = SignupAPIView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)


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


class ChangePasswordTest(TestCase):
    def test_with_user(self):
        user = UserF.create()
        view = ChangePassword.as_view()
        url = reverse('admin:changepassword')
        request = APIRequestFactory().get(url)
        request.user = user
        response = view(request).render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_anonymous(self):
        user = AnonymousUser()
        view = ChangePassword.as_view()
        url = reverse('admin:changepassword')
        request = APIRequestFactory().get(url)
        request.user = user
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


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

    def delete(self, user):
        url = reverse('ajax:usergroup', kwargs={
            'project_id': self.project.id,
            'group_id': self.contributors.id
        })
        request = self.factory.delete(url)
        force_authenticate(request, user=user)
        view = UserGroup.as_view()

        return view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id).render()

    def test_update_description_with_admin(self):
        response = self.put(self.admin, {'description': 'new description'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Group.objects.get(pk=self.contributors.id).description,
            'new description')

    def test_update_description_with_contributor(self):
        response = self.put(
            self.contributor, {'description': 'new description'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Group.objects.get(pk=self.contributors.id).description,
            'new description')

    def test_update_description_with_non_member(self):
        response = self.put(
            self.non_member, {'description': 'new description'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(
            Group.objects.get(pk=self.contributors.id).description,
            'new description')

    @raises(Group.DoesNotExist)
    def test_delete_description_with_admin(self):
        response = self.delete(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        Group.objects.get(pk=self.contributors.id)

    def test_delete_description_with_contributor(self):
        response = self.delete(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        Group.objects.get(pk=self.contributors.id)

    def test_delete_description_with_non_member(self):
        response = self.delete(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        Group.objects.get(pk=self.contributors.id)


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


class UserGroupViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{'project': self.project}
        )

        self.view = GroupingFactory(**{
            'project': self.project
        })

    def post(self, user, grouping_id=None):
        url = reverse('ajax:usergroup_views', kwargs={
            'project_id': self.project.id,
            'group_id': self.contributors.id
        })
        request = self.factory.post(
            url,
            json.dumps({"grouping": grouping_id or self.view.id}),
            content_type='application/json'
        )
        force_authenticate(request, user=user)
        view = UserGroupViews.as_view()

        return view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id).render()

    def test_add_not_existing_view(self):
        view = GroupingFactory.create()
        response = self.post(self.admin, grouping_id=view.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_view_with_admin(self):
        response = self.post(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, grouping=self.view).count(), 1)

    def test_add_view_with_contributor(self):
        response = self.post(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, grouping=self.view).count(), 0)

    def test_add_view_with_non_member(self):
        response = self.post(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, grouping=self.view).count(), 0)


class UserGroupSingleViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{'project': self.project}
        )

        self.view = GroupingFactory(**{
            'project': self.project
        })

        GroupingUserGroupFactory(**{
            'usergroup': self.contributors,
            'grouping': self.view
        })

    def put(self, user, data):
        url = reverse('ajax:usergroup_single_view', kwargs={
            'project_id': self.project.id,
            'group_id': self.contributors.id,
            'grouping_id': self.view.id
        })
        request = self.factory.put(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = UserGroupSingleView.as_view()

        return view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id,
            grouping_id=self.view.id).render()

    def delete(self, user, view_to_delete=None):
        the_view = view_to_delete or self.view
        url = reverse('ajax:usergroup_single_view', kwargs={
            'project_id': self.project.id,
            'group_id': self.contributors.id,
            'grouping_id': the_view.id
        })
        request = self.factory.delete(url)
        force_authenticate(request, user=user)
        view = UserGroupSingleView.as_view()

        return view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id,
            grouping_id=the_view.id).render()

    def test_delete_not_existing_viewgroup(self):
        response = self.delete(
            self.admin,
            view_to_delete=GroupingFactory.create()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_with_admin(self):
        response = self.delete(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, grouping=self.view).count(), 0)

    def test_delete_with_contributor(self):
        response = self.delete(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, grouping=self.view).count(), 1)

    def test_delete_with_non_member(self):
        response = self.delete(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, grouping=self.view).count(), 1)

    def test_update_partial_with_admin(self):
        response = self.put(self.admin, {'can_moderate': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        view_group = self.contributors.viewgroups.get(
            usergroup=self.contributors, grouping=self.view)
        self.assertTrue(view_group.can_read)
        self.assertTrue(view_group.can_view)

    def test_update_conplete_with_admin(self):
        response = self.put(
            self.admin,
            {'can_read': True, 'can_view': False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        view_group = self.contributors.viewgroups.get(
            usergroup=self.contributors, grouping=self.view)
        self.assertTrue(view_group.can_read)
        self.assertFalse(view_group.can_view)

    def test_update_with_contributor(self):
        response = self.put(self.contributor, {'can_moderate': True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        view_group = self.contributors.viewgroups.get(
            usergroup=self.contributors, grouping=self.view)
        self.assertTrue(view_group.can_read)
        self.assertTrue(view_group.can_view)

    def test_update_with_non_member(self):
        response = self.put(self.non_member, {'can_moderate': True})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        view_group = self.contributors.viewgroups.get(
            usergroup=self.contributors, grouping=self.view)
        self.assertTrue(view_group.can_read)
        self.assertTrue(view_group.can_view)
