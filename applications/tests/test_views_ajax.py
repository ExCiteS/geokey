import json

from django.test import TestCase

from nose.tools import raises

from projects.tests.model_factories import UserF

from ..models import Application

from .model_factories import ApplicationFactory


class ApplicationAjaxTest(TestCase):
    def setUp(self):
        self.creator = UserF.create(**{'password': '1'})
        self.user = UserF.create(**{'password': '1'})

        self.application = ApplicationFactory(**{
            'creator': self.creator
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

    def test_update_descrtiption_with_creator(self):
        response = self._put(
            '/ajax/apps/' + str(self.application.id) + '/',
            {'description': 'bockwurst'},
            self.creator
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Application.objects.get(pk=self.application.id).description,
            'bockwurst'
        )

    def test_update_descrtiption_with_user(self):
        response = self._put(
            '/ajax/apps/' + str(self.application.id) + '/',
            {'description': 'bockwurst'},
            self.user
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Application.objects.get(pk=self.application.id).description,
            'bockwurst'
        )

    @raises(Application.DoesNotExist)
    def test_delete_with_creator(self):
        response = self._delete(
            '/ajax/apps/' + str(self.application.id) + '/',
            self.creator
        )
        self.assertEqual(response.status_code, 204)
        Application.objects.get(pk=self.application.id)

    def test_delete_with_user(self):
        response = self._delete(
            '/ajax/apps/' + str(self.application.id) + '/',
            self.user
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Application.objects.get(pk=self.application.id),
            self.application
        )
