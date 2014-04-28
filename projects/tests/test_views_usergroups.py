import json

from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate

from .model_factories import UserF, UserGroupF, ProjectF
from ..models import Project
from ..views import ProjectApiUserGroup, ProjectApiUserGroupUser


class ProjectUsergroupTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.user_to_add = UserF.create()
        self.admin_to_remove = UserF.create()
        self.contrib_to_remove = UserF.create()
        self.some_user = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[
                self.admin, self.admin_to_remove
            ]),
            'contributors': UserGroupF(add_users=[
                self.contributor, self.contrib_to_remove
            ])
        })

    def post(self, data, group, user):
        self.client.login(username=user.username, password='1')
        return self.client.post(
            '/ajax/projects/' + str(self.project.id) + '/usergroups/' +
            str(group) + '/users/',
            json.dumps(data),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    def delete(self, user_to_remove, group, user):
        self.client.login(username=user.username, password='1')
        return self.client.delete(
            '/ajax/projects/' + str(self.project.id) + '/usergroups/' +
            str(group) + '/users/' +
            str(user_to_remove.id) + '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    #
    #
    #
    # ADD USERS
    #

    def test_add_to_not_existing_usergroup(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' % (self.project.id, 6545454844545648),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiUserGroup.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=6545454844545648
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_add_not_existing_user(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' % (self.project.id, self.project.admins.id),
            {'userId': 4445468756454}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiUserGroup.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.admins.id
        ).render()

        self.assertEqual(response.status_code, 400)

    def test_add_admin_with_admin(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' % (self.project.id, self.project.admins.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiUserGroup.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.admins.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            self.user_to_add,
            Project.objects.get(
                pk=self.project.id).admins.users.all()
        )

    def test_add_admin_with_contributor(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' % (self.project.id, self.project.admins.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.contributor)
        view = ProjectApiUserGroup.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.admins.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(
                pk=self.project.id).admins.users.all()
        )

    def test_add_admin_with_non_member(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' % (self.project.id, self.project.admins.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.non_member)
        view = ProjectApiUserGroup.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.admins.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(
                pk=self.project.id).admins.users.all()
        )

    def test_add_contributor_with_admin(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' % (self.project.id, self.project.contributors.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiUserGroup.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.contributors.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            self.user_to_add,
            Project.objects.get(
                pk=self.project.id).contributors.users.all()
        )

    def test_add_contributor_with_contributor(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' % (self.project.id, self.project.contributors.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.contributor)
        view = ProjectApiUserGroup.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.contributors.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(
                pk=self.project.id).contributors.users.all()
        )

    def test_add_contributor_with_non_member(self):
        request = self.factory.post(
            '/ajax/projects/%s/usergroups/%s/users/' % (self.project.id, self.project.contributors.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.non_member)
        view = ProjectApiUserGroup.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.contributors.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(
                pk=self.project.id).contributors.users.all()
        )

    #
    #
    #
    # REMOVE USERS
    #

    def test_delete_not_existing_user(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.project.admins.id, self.some_user.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiUserGroupUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.contributors.id,
            user_id=self.some_user.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_from_not_existing_usergroup(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, 455646445484545, self.admin_to_remove),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiUserGroupUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=455646445484545,
            user_id=self.admin_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_adminuser_with_admin(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.project.admins.id, self.admin_to_remove.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiUserGroupUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.admins.id,
            user_id=self.admin_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertNotIn(
            self.admin_to_remove,
            Project.objects.get(
                pk=self.project.id).admins.users.all()
        )

    def test_delete_adminuser_with_contributor(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.project.admins.id, self.admin_to_remove.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.contributor)
        view = ProjectApiUserGroupUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.admins.id,
            user_id=self.admin_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.admin_to_remove,
            Project.objects.get(
                pk=self.project.id).admins.users.all()
        )

    def test_delete_adminuser_with_non_member(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.project.admins.id, self.admin_to_remove.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.non_member)
        view = ProjectApiUserGroupUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.admins.id,
            user_id=self.admin_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.admin_to_remove,
            Project.objects.get(
                pk=self.project.id).admins.users.all()
        )

    def test_delete_contributor_with_admin(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.project.contributors.id, self.contrib_to_remove.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiUserGroupUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.contributors.id,
            user_id=self.contrib_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertNotIn(
            self.contrib_to_remove,
            Project.objects.get(
                pk=self.project.id).contributors.users.all()
        )

    def test_delete_contributor_with_contributor(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.project.contributors.id, self.contrib_to_remove.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.contributor)
        view = ProjectApiUserGroupUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.contributors.id,
            user_id=self.contrib_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.contrib_to_remove,
            Project.objects.get(
                pk=self.project.id).contributors.users.all()
        )

    def test_delete_contributor_with_non_member(self):
        request = self.factory.delete(
            '/ajax/projects/%s/usergroups/%s/users/%s/' %
            (self.project.id, self.project.contributors.id, self.contrib_to_remove.id),
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.non_member)
        view = ProjectApiUserGroupUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            group_id=self.project.contributors.id,
            user_id=self.contrib_to_remove.id
        ).render()
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.contrib_to_remove,
            Project.objects.get(
                pk=self.project.id).contributors.users.all()
        )
