import json

from django.test import TestCase

from nose.tools import raises

from projects.tests.model_factories import UserF, UserGroupF, ProjectF

from .model_factories import ViewFactory, ViewGroupFactory
from ..models import ViewGroup


class ViewGroupAjaxTest(TestCase):
    def setUp(self):
        self.creator = UserF.create(**{'password': '1'})
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})
        self.view_user = UserF.create(**{'password': '1'})

        self.project = ProjectF.create(**{
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.view = ViewFactory(**{
            'project': self.project
        })
        self.group = ViewGroupFactory(add_users=[self.view_user], **{
            'view': self.view,
            'description': 'bockwurst'
        })

    def _put(self, url, data, user):
        self.client.login(username=user.username, password='1')
        return self.client.put(
            url,
            json.dumps(data),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    def _delete(self, url, user):
        self.client.login(username=user.username, password='1')
        return self.client.delete(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    def test_update_description_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id) + '/usergroups/' + str(self.group.id),
            {'description': 'new description'},
            self.creator
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.project.id).description,
            'new description'
        )

    @raises(ViewGroup.DoesNotExist)
    def test_delete_with_admin(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id) + '/usergroups/' + str(self.group.id),
            self.creator
        )
        self.assertEqual(response.status_code, 204)
        ViewGroup.objects.get(pk=self.project.id)

    def test_update_description_with_contributor(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id) + '/usergroups/' + str(self.group.id),
            {'description': 'new description'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.project.id).description,
            'bockwurst'
        )

    def test_delete_with_contributor(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id) + '/usergroups/' + str(self.group.id),
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.project.id).status, 'active'
        )

    def test_update_description_with_non_member(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id) + '/usergroups/' + str(self.group.id),
            {'description': 'new description'},
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.project.id).description,
            'bockwurst'
        )

    def test_delete_with_non_member(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id) + '/usergroups/' + str(self.group.id),
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.project.id).status, 'active'
        )

    def test_update_description_with_view_user(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id) + '/usergroups/' + str(self.group.id),
            {'description': 'new description'},
            self.view_user
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.project.id).description,
            'bockwurst'
        )

    def test_delete_with_view_user(self):
        response = self._delete(
            '/ajax/projects/' + str(self.project.id) + '/views/' + str(self.view.id) + '/usergroups/' + str(self.group.id),
            self.view_user
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ViewGroup.objects.get(pk=self.project.id).status, 'active'
        )
