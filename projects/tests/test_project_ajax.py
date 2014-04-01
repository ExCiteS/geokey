import json

from django.test import TestCase

from nose.tools import raises

from .model_factories import UserF, UserGroupF, ProjectF
from ..models import Project


class ProjectAjaxTest(TestCase):
    def setUp(self):
        self.creator = UserF.create(**{'password': '1'})
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})

        self.project = ProjectF.create(**{
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })

    def _put(self, url, data, user):
        self.client.login(username=user.username, password='1')
        return self.client.put(
            url + '/',
            json.dumps(data),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    def _delete(self, url, user):
        self.client.login(username=user.username, password='1')
        return self.client.delete(
            url + '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    def test_unauthenticated(self):
        response = self.client.put(
            '/ajax/projects/' + str(self.project.id) + '/',
            {'status': 'bockwurst'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_update_with_wrong_status(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id),
            {'status': 'bockwurst'},
            self.creator
        )
        self.assertEqual(response.status_code, 400)

    def test_update_project_status_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id),
            {'status': 'inactive'},
            self.creator
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).status,
            'inactive'
        )

    def test_update_project_description_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id),
            {'description': 'new description'},
            self.creator
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).description,
            'new description'
        )

    def test_update_project_description_with_contributor(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id),
            {'description': 'new description'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).description,
            self.project.description
        )

    def test_update_project_description_with_non_member(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id),
            {'description': 'new description'},
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).description,
            self.project.description
        )

    @raises(Project.DoesNotExist)
    def test_delete_project_with_admin(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id),
            self.admin
        )
        self.assertEqual(response.status_code, 204)
        Project.objects.get(pk=self.project.id)

    def test_delete_project_with_contributor(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id),
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).status,
            'active'
        )

    def test_delete_project_with_non_member(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id),
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).status,
            'active'
        )
