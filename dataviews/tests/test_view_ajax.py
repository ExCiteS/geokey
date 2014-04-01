import json

from django.test import TestCase

from nose.tools import raises

from projects.tests.model_factories import ProjectF, UserF, UserGroupF

from ..models import View

from .model_factories import ViewFactory, ViewGroupFactory


class ViewAjaxTest(TestCase):
    def setUp(self):
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})
        self.view_member = UserF.create(**{'password': '1'})

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.view = ViewFactory(**{
            'project': self.project,
            'description': 'description'
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': self.view
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

    def test_update_description_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id),
            {'description': 'bockwurst'},
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(View.objects.get(pk=self.view.id).description, 'bockwurst')

    @raises(View.DoesNotExist)
    def test_delete_with_admin(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id),
            self.admin
        )
        self.assertEqual(response.status_code, 204)
        View.objects.get(pk=self.view.id)

    def test_update_description_with_contributor(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id),
            {'description': 'bockwurst'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).description, 'description')

    def test_delete_with_contributor(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id),
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).status, 'active')

    def test_update_description_with_non_member(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id),
            {'description': 'bockwurst'},
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).description, 'description')

    def test_delete_with_non_member(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id),
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).status, 'active')

    def test_update_description_with_view_member(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id),
            {'description': 'bockwurst'},
            self.view_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).description, 'description')

    def test_delete_with_view_member(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id),
            self.view_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).status, 'active')
