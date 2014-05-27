import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from nose.tools import raises

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from projects.tests.model_factories import ProjectF
from dataviews.tests.model_factories import ViewFactory

from .model_factories import UserF, UserGroupF, ViewUserGroupFactory
from ..views import (
    UserGroup, UserGroupUsers, UserGroupSingleUser, UserGroupViews,
    UserGroupSingleView, UserGroupCreate, UserGroupSettings, UserProfile
)
from ..models import UserGroup as Group


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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
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

        self.assertEqual(response.status_code, 403)
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
        self.assertEqual(response.status_code, 403)
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

        self.view = ViewFactory(**{
            'project': self.project
        })

    def post(self, user, view_id=None):
        url = reverse('ajax:usergroup_views', kwargs={
            'project_id': self.project.id,
            'group_id': self.contributors.id
        })
        request = self.factory.post(
            url,
            json.dumps({"view": view_id or self.view.id}),
            content_type='application/json'
        )
        force_authenticate(request, user=user)
        view = UserGroupViews.as_view()

        return view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id).render()

    def test_add_not_existing_user(self):
        view = ViewFactory.create()
        response = self.post(self.admin, view_id=view.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_view_with_admin(self):
        response = self.post(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, view=self.view).count(), 1)

    def test_add_view_with_contributor(self):
        response = self.post(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, view=self.view).count(), 0)

    def test_add_view_with_non_member(self):
        response = self.post(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, view=self.view).count(), 0)


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

        self.view = ViewFactory(**{
            'project': self.project
        })

        ViewUserGroupFactory(**{
            'usergroup': self.contributors,
            'view': self.view
        })

    def put(self, user, data):
        url = reverse('ajax:usergroup_single_view', kwargs={
            'project_id': self.project.id,
            'group_id': self.contributors.id,
            'view_id': self.view.id
        })
        request = self.factory.put(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = UserGroupSingleView.as_view()

        return view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id,
            view_id=self.view.id).render()

    def delete(self, user, view_to_delete=None):
        the_view = view_to_delete or self.view
        url = reverse('ajax:usergroup_single_view', kwargs={
            'project_id': self.project.id,
            'group_id': self.contributors.id,
            'view_id': the_view.id
        })
        request = self.factory.delete(url)
        force_authenticate(request, user=user)
        view = UserGroupSingleView.as_view()

        return view(
            request,
            project_id=self.project.id,
            group_id=self.contributors.id,
            view_id=the_view.id).render()

    def test_delete_not_existing_viewgroup(self):
        response = self.delete(self.admin, view_to_delete=ViewFactory.create())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_with_admin(self):
        response = self.delete(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, view=self.view).count(), 0)

    def test_delete_with_contributor(self):
        response = self.delete(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, view=self.view).count(), 1)

    def test_delete_with_non_member(self):
        response = self.delete(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.contributors.viewgroups.filter(
                usergroup=self.contributors, view=self.view).count(), 1)

    def test_update_partial_with_admin(self):
        response = self.put(self.admin, {'can_moderate': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        view_group = self.contributors.viewgroups.get(
            usergroup=self.contributors, view=self.view)
        self.assertTrue(view_group.can_moderate)
        self.assertFalse(view_group.can_read)
        self.assertTrue(view_group.can_view)

    def test_update_conplete_with_admin(self):
        response = self.put(
            self.admin,
            {'can_moderate': True, 'can_read': True, 'can_view': False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        view_group = self.contributors.viewgroups.get(
            usergroup=self.contributors, view=self.view)
        self.assertTrue(view_group.can_moderate)
        self.assertTrue(view_group.can_read)
        self.assertFalse(view_group.can_view)

    def test_update_with_contributor(self):
        response = self.put(self.contributor, {'can_moderate': True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        view_group = self.contributors.viewgroups.get(
            usergroup=self.contributors, view=self.view)
        self.assertFalse(view_group.can_moderate)
        self.assertFalse(view_group.can_read)
        self.assertTrue(view_group.can_view)

    def test_update_with_non_member(self):
        response = self.put(self.non_member, {'can_moderate': True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        view_group = self.contributors.viewgroups.get(
            usergroup=self.contributors, view=self.view)
        self.assertFalse(view_group.can_moderate)
        self.assertFalse(view_group.can_read)
        self.assertTrue(view_group.can_view)


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
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
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
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
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
