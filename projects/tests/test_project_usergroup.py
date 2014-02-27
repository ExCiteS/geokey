import json

from django.test import TestCase

from .model_factories import UserF, UserGroupF, ProjectF
from ..models import Project


class ProjectUsergroupTest(TestCase):
    def setUp(self):
        self.creator = UserF.create(**{'password': '1'})
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})
        self.user_to_add = UserF.create()
        self.admin_to_remove = UserF.create()
        self.contrib_to_remove = UserF.create()
        self.some_user = UserF.create()

        self.project = ProjectF.create(**{
            'creator': self.creator,
            'admins': UserGroupF(add_users=[
                self.creator, self.admin, self.admin_to_remove
            ]),
            'contributors': UserGroupF(add_users=[
                self.contributor, self.contrib_to_remove
            ])
        })

    def post(self, data, group, user):
        self.client.login(username=user.username, password='1')
        return self.client.post(
            '/ajax/projects/' + str(self.project.id) + '/usergroups/' +
            str(group) + '/users',
            json.dumps(data),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    def delete(self, user_to_remove, group, user):
        self.client.login(username=user.username, password='1')
        return self.client.delete(
            '/ajax/projects/' + str(self.project.id) + '/usergroups/' +
            str(group) + '/users/' +
            str(user_to_remove.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    #
    #
    #
    # ADD USERS
    #

    def test_add_to_not_existing_usergroup(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            6545454844545648,
            self.admin)
        self.assertEqual(response.status_code, 404)

    def test_add_not_existing_user(self):
        response = self.post(
            {'userId': 4445468756454},
            self.project.admins.id,
            self.admin)
        self.assertEqual(response.status_code, 400)

    def test_add_admin_with_admin(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.project.admins.id,
            self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '"username": "' + self.user_to_add.username + '"'
        )
        self.assertIn(
            self.user_to_add,
            Project.objects.get(
                self.admin,
                pk=self.project.id).admins.users.all()
        )

    def test_add_admin_with_contributor(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.project.admins.id,
            self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(
                self.admin,
                pk=self.project.id).admins.users.all()
        )

    def test_add_admin_with_non_member(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.project.admins.id,
            self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(
                self.admin,
                pk=self.project.id).admins.users.all()
        )

    def test_add_contributor_with_admin(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.project.contributors.id,
            self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '"username": "' + self.user_to_add.username + '"'
        )
        self.assertIn(
            self.user_to_add,
            Project.objects.get(
                self.admin,
                pk=self.project.id).contributors.users.all()
        )

    def test_add_contributor_with_contributor(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.project.contributors.id,
            self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(
                self.admin,
                pk=self.project.id).contributors.users.all()
        )

    def test_add_contributor_with_non_member(self):
        response = self.post(
            {'userId': self.user_to_add.id},
            self.project.contributors.id,
            self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(
                self.admin,
                pk=self.project.id).contributors.users.all()
        )

    #
    #
    #
    # REMOVE USERS
    #

    def test_delete_not_existing_user(self):
        response = self.delete(
            self.some_user,
            self.project.admins.id,
            self.admin)
        self.assertEqual(response.status_code, 404)

    def test_delete_from_not_existing_usergroup(self):
        response = self.delete(
            self.admin_to_remove,
            455646445484545,
            self.admin)
        self.assertEqual(response.status_code, 404)

    def test_delete_adminuser_with_admin(self):
        response = self.delete(
            self.admin_to_remove,
            self.project.admins.id,
            self.admin)
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(
            self.admin_to_remove,
            Project.objects.get(
                self.admin,
                pk=self.project.id).admins.users.all()
        )

    def test_delete_adminuser_with_contributor(self):
        response = self.delete(
            self.admin_to_remove,
            self.project.admins.id,
            self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.admin_to_remove,
            Project.objects.get(
                self.admin,
                pk=self.project.id).admins.users.all()
        )

    def test_delete_adminuser_with_non_member(self):
        response = self.delete(
            self.admin_to_remove,
            self.project.admins.id,
            self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.admin_to_remove,
            Project.objects.get(
                self.admin,
                pk=self.project.id).admins.users.all()
        )

    def test_delete_contributor_with_admin(self):
        response = self.delete(
            self.contrib_to_remove,
            self.project.contributors.id,
            self.admin)
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(
            self.contrib_to_remove,
            Project.objects.get(
                self.admin,
                pk=self.project.id).contributors.users.all()
        )

    def test_delete_contributor_with_contributor(self):
        response = self.delete(
            self.contrib_to_remove,
            self.project.contributors.id,
            self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.contrib_to_remove,
            Project.objects.get(
                self.admin,
                pk=self.project.id).contributors.users.all()
        )

    def test_delete_contributor_with_non_member(self):
        response = self.delete(
            self.contrib_to_remove,
            self.project.contributors.id,
            self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.contrib_to_remove,
            Project.objects.get(
                self.admin,
                pk=self.project.id).contributors.users.all()
        )
