from django.core.urlresolvers import reverse
from django.test import TestCase

from nose.tools import raises
from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, UserGroupF, ProjectF

from .model_factories import ViewFactory, ViewGroupFactory
from ..models import ViewGroup
from ..views import (
    ViewUserGroupUsersApi, ViewUserGroupApiDetail, ViewUserGroupUsersApiDetail
)


class UpdateViewGroupTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_user = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.view = ViewFactory(**{
            'project': self.project
        })
        self.group = ViewGroupFactory(
            add_users=[self.view_user],
            **{
                'view': self.view,
                'description': 'bockwurst'
            }
        )

    def put(self, data, user):
        url = reverse('ajax:view_group', kwargs={
            'project_id': self.project.id,
            'view_id': self.view.id,
            'group_id': self.group.id
        })
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        theview = ViewUserGroupApiDetail.as_view()
        return theview(
            request,
            project_id=self.project.id,
            view_id=self.view.id,
            group_id=self.group.id).render()

    def test_update_description_with_admin(self):
        response = self.put({'description': 'new description'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.group.id).description,
            'new description'
        )

    def test_update_description_with_contributor(self):
        response = self.put(
            {'description': 'new description'}, self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.group.id).description,
            'bockwurst'
        )

    def test_update_description_with_non_member(self):
        response = self.put(
            {'description': 'new description'}, self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.group.id).description,
            'bockwurst'
        )

    def test_update_description_with_view_user(self):
        response = self.put({'description': 'new description'}, self.view_user)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.group.id).description,
            'bockwurst'
        )


class TestDeleteUserGroupTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_user = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.view = ViewFactory(**{
            'project': self.project
        })
        self.group = ViewGroupFactory(
            add_users=[self.view_user],
            **{
                'view': self.view,
                'description': 'bockwurst'
            }
        )

    def delete(self, user):
        url = reverse('ajax:view_group', kwargs={
            'project_id': self.project.id,
            'view_id': self.view.id,
            'group_id': self.group.id
        })
        request = self.factory.delete(url)
        force_authenticate(request, user=user)
        theview = ViewUserGroupApiDetail.as_view()
        return theview(
            request,
            project_id=self.project.id,
            view_id=self.view.id,
            group_id=self.group.id).render()

    @raises(ViewGroup.DoesNotExist)
    def test_delete_with_admin(self):
        response = self.delete(self.admin)
        self.assertEqual(response.status_code, 204)
        ViewGroup.objects.get(pk=self.group.id)

    def test_delete_with_contributor(self):
        response = self.delete(self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.group.id).status, 'active'
        )

    def test_delete_with_non_member(self):
        response = self.delete(self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.group.id).status, 'active'
        )

    def test_delete_with_view_user(self):
        response = self.delete(self.view_user)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.group.id).status, 'active'
        )


class AddUserToGroup(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_user = UserF.create()
        self.user_to_add = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.view = ViewFactory(**{
            'project': self.project
        })
        self.group = ViewGroupFactory(
            add_users=[self.view_user],
            **{
                'view': self.view,
                'description': 'bockwurst'
            }
        )

    def post(self, data, user):
        url = reverse('ajax:view_group_users', kwargs={
            'project_id': self.project.id,
            'view_id': self.view.id,
            'group_id': self.group.id
        })
        request = self.factory.post(url, data)
        force_authenticate(request, user=user)
        theview = ViewUserGroupUsersApi.as_view()
        return theview(
            request,
            project_id=self.project.id,
            view_id=self.view.id,
            group_id=self.group.id).render()

    def test_add_not_existing_user(self):
        response = self.post(
            {'userId': 54545454541456454},
            self.admin
        )
        self.assertEqual(response.status_code, 400)

    def test_add_user_with_admin(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.admin
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            self.user_to_add,
            ViewGroup.objects.get(pk=self.group.id).users.all()
        )

    def test_add_user_with_contributor(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            ViewGroup.objects.get(pk=self.group.id).users.all()
        )

    def test_add_user_with_non_member(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            ViewGroup.objects.get(pk=self.group.id).users.all()
        )

    def test_add_user_with_view_member(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            ViewGroup.objects.get(pk=self.group.id).users.all()
        )


class DeleteUserFromGroup(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_user = UserF.create()
        self.user_to_remove = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.view = ViewFactory(**{
            'project': self.project
        })
        self.group = ViewGroupFactory(
            add_users=[self.view_user, self.user_to_remove],
            **{
                'view': self.view,
                'description': 'bockwurst'
            }
        )

    def delete(self, user):
        url = reverse('ajax:view_group_users_user', kwargs={
            'project_id': self.project.id,
            'view_id': self.view.id,
            'group_id': self.group.id,
            'user_id': self.user_to_remove.id
        })
        request = self.factory.delete(url)
        force_authenticate(request, user=user)
        theview = ViewUserGroupUsersApiDetail.as_view()
        return theview(
            request,
            project_id=self.project.id,
            view_id=self.view.id,
            group_id=self.group.id,
            user_id=self.user_to_remove.id).render()

    def test_remove_not_existing_user(self):
        url = reverse('ajax:view_group_users_user', kwargs={
            'project_id': self.project.id,
            'view_id': self.view.id,
            'group_id': self.group.id,
            'user_id': self.contributor.id
        })
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        theview = ViewUserGroupUsersApiDetail.as_view()
        response = theview(
            request,
            project_id=self.project.id,
            view_id=self.view.id,
            group_id=self.group.id,
            user_id=self.contributor.id).render()
        self.assertEqual(response.status_code, 404)

    def test_remove_user_with_admin(self):
        response = self.delete(self.admin)
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(
            self.user_to_remove,
            ViewGroup.objects.get(pk=self.group.id).users.all()
        )

    def test_remove_user_with_contributor(self):
        response = self.delete(self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.user_to_remove,
            ViewGroup.objects.get(pk=self.group.id).users.all()
        )

    def test_remove_user_with_non_member(self):
        response = self.delete(self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.user_to_remove,
            ViewGroup.objects.get(pk=self.group.id).users.all()
        )

    def test_remove_user_with_view_member(self):
        response = self.delete(self.view_user)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.user_to_remove,
            ViewGroup.objects.get(pk=self.group.id).users.all()
        )
