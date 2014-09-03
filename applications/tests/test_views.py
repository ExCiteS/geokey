from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from rest_framework.test import APIRequestFactory, force_authenticate

from nose.tools import raises

from projects.tests.model_factories import UserF

from ..models import Application
from ..views import (
    ApplicationOverview, ApplicationCreate, ApplicationSettings,
    ApplicationUpdate
)

from .model_factories import ApplicationFactory


class ApplicationOverviewTest(TestCase):
    def test_get_with_user(self):
        view = ApplicationOverview.as_view()
        url = reverse('admin:app_overview')
        request = APIRequestFactory().get(url)
        request.user = UserF.create()
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_anonymous(self):
        view = ApplicationOverview.as_view()
        url = reverse('admin:app_overview')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class ApplicationCreateTest(TestCase):
    def test_get_with_user(self):
        view = ApplicationCreate.as_view()
        url = reverse('admin:app_register')
        request = APIRequestFactory().get(url)
        request.user = UserF.create()
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_anonymous(self):
        view = ApplicationCreate.as_view()
        url = reverse('admin:app_register')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class ApplicationSettingsTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.app = ApplicationFactory.create(**{'creator': self.creator})

    def test_get_with_creator(self):
        view = ApplicationSettings.as_view()
        url = reverse('admin:app_settings', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().get(url)
        request.user = self.creator
        response = view(request, app_id=self.app.id).render()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'You are not the owner of this application and therefore not'
            'allowed to access this app.'
        )

    def test_get_with_user(self):
        view = ApplicationSettings.as_view()
        url = reverse('admin:app_settings', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().get(url)
        request.user = UserF.create()
        response = view(request, app_id=self.app.id).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'You are not the owner of this application and therefore not '
            'allowed to access this app.'
        )

    def test_get_with_anonymous(self):
        view = ApplicationSettings.as_view()
        url = reverse('admin:app_settings', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request, app_id=self.app.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


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
