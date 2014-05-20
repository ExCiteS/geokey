import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from projects.tests.model_factories import ProjectF
from dataviews.tests.model_factories import ViewFactory

from .model_factories import UserF, UserGroupF, ViewUserGroupFactory
from ..views import (
    UserGroup, UserGroupUser, UserGroupViews, UserGroupSingleView
)


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

    def test_add_to_not_existing_usergroup(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' %
            (self.project.id, 6545454844545648),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = UserGroup.as_view()
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
        view = UserGroup.as_view()
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
        view = UserGroup.as_view()
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
        view = UserGroup.as_view()
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
        view = UserGroup.as_view()
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


class UserGroupUserTest(TestCase):
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
        view = UserGroupUser.as_view()
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
        view = UserGroupUser.as_view()
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
        view = UserGroupUser.as_view()
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
        view = UserGroupUser.as_view()
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
        view = UserGroupUser.as_view()
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
