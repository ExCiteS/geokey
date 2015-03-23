from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from nose.tools import raises

from oauth2_provider.models import AccessToken
from rest_framework.test import APIRequestFactory

from geokey.projects.tests.model_factories import UserF

from ..views import (
    ApplicationOverview, ApplicationCreate, ApplicationSettings,
    ApplicationDelete, ApplicationConnected, ApplicationDisconnect
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


class ApplicationConnectedTest(TestCase):
    def test_get_with_user(self):
        view = ApplicationConnected.as_view()
        url = reverse('admin:app_connected')
        request = APIRequestFactory().get(url)

        request.user = UserF.create()
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_anonymous(self):
        view = ApplicationConnected.as_view()
        url = reverse('admin:app_connected')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class ApplicationDisconnectTest(TestCase):
    def setUp(self):
        self.user = UserF.create()
        self.app = ApplicationFactory.create()
        self.token = AccessToken.objects.create(
            user=self.user,
            application=self.app,
            token='df0af6a395b4cd072445b3832e9379bfee257da0',
            scope=1,
            expires='2030-12-31 23:59'
        )

    @raises(AccessToken.DoesNotExist)
    def test_get_with_user(self):
        view = ApplicationDisconnect.as_view()
        url = reverse('admin:app_disconnect', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().get(url)

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        request.user = self.user
        response = view(request, app_id=self.app.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        AccessToken.objects.get(pk=self.token.id)

    def test_get_with_anonymous(self):
        view = ApplicationDisconnect.as_view()
        url = reverse('admin:app_disconnect', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request, app_id=self.app.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertIsNotNone(AccessToken.objects.get(pk=self.token.id))

    def test_get_with_unconnected_user(self):
        view = ApplicationDisconnect.as_view()
        url = reverse('admin:app_disconnect', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().get(url)
        request.user = UserF.create()
        response = view(request, app_id=self.app.id)
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
        self.app = ApplicationFactory.create(**{'user': self.creator})

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


class ApplicationDeleteTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.app = ApplicationFactory.create(**{'user': self.creator})

    def test_get_with_creator(self):
        view = ApplicationDelete.as_view()
        url = reverse('admin:app_delete', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().get(url)

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        request.user = self.creator
        response = view(request, app_id=self.app.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_with_user(self):
        view = ApplicationDelete.as_view()
        url = reverse('admin:app_delete', kwargs={'app_id': self.app.id})
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
        view = ApplicationDelete.as_view()
        url = reverse('admin:app_delete', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request, app_id=self.app.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
