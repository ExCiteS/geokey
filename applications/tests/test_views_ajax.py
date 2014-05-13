from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from nose.tools import raises

from projects.tests.model_factories import UserF

from ..models import Application
from ..views import ApplicationUpdate

from .model_factories import ApplicationFactory


class ApplicationAjaxTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.creator = UserF.create()
        self.user = UserF.create()

        self.application = ApplicationFactory(**{
            'creator': self.creator
        })

    def _put(self, user):
        request = self.factory.put(
            '/ajax/apps/%s/' % self.application.id,
            {'description': 'bockwurst'}
        )
        force_authenticate(request, user=user)
        view = ApplicationUpdate.as_view()
        return view(request, app_id=self.application.id).render()

    def _delete(self, user):
        request = self.factory.delete('/ajax/apps/%s/' % self.application.id)
        force_authenticate(request, user=user)
        view = ApplicationUpdate.as_view()
        return view(request, app_id=self.application.id).render()

    def test_update_descrtiption_with_creator(self):
        response = self._put(self.creator)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Application.objects.get(pk=self.application.id).description,
            'bockwurst'
        )

    def test_update_descrtiption_with_user(self):
        response = self._put(self.user)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            Application.objects.get(pk=self.application.id).description,
            'bockwurst'
        )

    @raises(Application.DoesNotExist)
    def test_delete_with_creator(self):
        response = self._delete(self.creator)
        self.assertEqual(response.status_code, 204)
        Application.objects.get(pk=self.application.id)

    def test_delete_with_user(self):
        response = self._delete(self.user)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Application.objects.get(pk=self.application.id),
            self.application
        )
