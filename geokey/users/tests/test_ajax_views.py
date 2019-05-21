"""Tests for AJAX views of users."""

import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from geokey.projects.tests.model_factories import ProjectFactory

from .model_factories import UserFactory, UserGroupFactory
from ..views import (
    UserGroup, UserGroupUsers, UserGroupSingleUser,
)
from ..models import UserGroup as Group


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

        self.assertEqual(response.status_code, 404)

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


class UserGroupSingleUserTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()
        self.contrib_to_remove = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin]
        )

        self.contributors = UserGroupFactory(
            add_users=[self.contributor, self.contrib_to_remove],
            **{'project': self.project, 'can_contribute': True}
        )

    def test_delete_not_existing_user(self):
        user = UserFactory.create()
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.contributors.id, user.id),
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupSingleUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.contributors.id,
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
            usergroup_id=455646445484545,
            user_id=self.contrib_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_on_locked_project(self):
        self.project.islocked = True
        self.project.save()

        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.contributors.id, self.contrib_to_remove.id),
        )
        force_authenticate(request, user=self.admin)
        view = UserGroupSingleUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            usergroup_id=self.contributors.id,
            user_id=self.contrib_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 400)

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
            usergroup_id=self.contributors.id,
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
            usergroup_id=self.contributors.id,
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
            usergroup_id=self.contributors.id,
            user_id=self.contrib_to_remove.id
        ).render()
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            self.contrib_to_remove,
            self.contributors.users.all()
        )
