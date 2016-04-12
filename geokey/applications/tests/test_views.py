"""Tests for views of applications."""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from nose.tools import raises

from oauth2_provider.models import AccessToken
from rest_framework.test import APIRequestFactory

from geokey.projects.tests.model_factories import UserFactory

from ..views import (
    ApplicationOverview, ApplicationCreate, ApplicationSettings,
    ApplicationDelete, ApplicationConnected, ApplicationDisconnect
)
from ..models import Application

from .model_factories import ApplicationFactory


class ApplicationOverviewTest(TestCase):
    def test_get_with_user(self):
        view = ApplicationOverview.as_view()
        url = reverse('admin:app_overview')
        request = APIRequestFactory().get(url)
        request.user = UserFactory.create()
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

        request.user = UserFactory.create()
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
        self.user = UserFactory.create()
        self.app = ApplicationFactory.create()
        self.token = AccessToken.objects.create(
            user=self.user,
            application=self.app,
            token='df0af6a395b4cd072445b3832e9379bfee257da0',
            scope=1,
            expires='2030-12-31T23:59:01+00:00'
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
        request.user = UserFactory.create()
        response = view(request, app_id=self.app.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class ApplicationCreateTest(TestCase):
    def test_get_with_user(self):
        view = ApplicationCreate.as_view()
        url = reverse('admin:app_register')
        request = APIRequestFactory().get(url)
        request.user = UserFactory.create()
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_anonymous(self):
        view = ApplicationCreate.as_view()
        url = reverse('admin:app_register')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_post_with_user(self):
        data = {
            'name': 'test app',
            'description:': '',
            'download_url': 'http://example.com',
            'redirect_uris': 'http://example.com',
            'authorization_grant_type': 'password'
        }
        view = ApplicationCreate.as_view()
        url = reverse('admin:app_register')
        request = APIRequestFactory().post(url, data)
        request.user = UserFactory.create()

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Application.objects.count(), 1)

    def test_post_with_anonymous(self):
        data = {
            'name': 'test app',
            'description': '',
            'download_url': 'http://example.com',
            'redirect_uris': 'http://example.com',
            'authorization_grant_type': 'password'
        }
        view = ApplicationCreate.as_view()
        url = reverse('admin:app_register')
        request = APIRequestFactory().post(url, data)
        request.user = AnonymousUser()

        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Application.objects.count(), 0)


class ApplicationSettingsTest(TestCase):
    def setUp(self):
        self.creator = UserFactory.create()
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
        request.user = UserFactory.create()
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

    def test_post_with_creator(self):
        data = {
            'name': 'test app',
            'description': '',
            'download_url': 'http://example.com',
            'redirect_uris': 'http://example.com',
            'authorization_grant_type': 'password'
        }
        view = ApplicationSettings.as_view()
        url = reverse('admin:app_settings', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().post(url, data)
        request.user = self.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request, app_id=self.app.id).render()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'You are not the owner of this application and therefore not'
            'allowed to access this app.'
        )

        ref = Application.objects.get(pk=self.app.id)
        self.assertEqual(ref.name, data.get('name'))
        self.assertEqual(ref.description, data.get('description'))
        self.assertEqual(ref.download_url, data.get('download_url'))
        self.assertEqual(ref.redirect_uris, data.get('redirect_uris'))
        self.assertEqual(
            ref.authorization_grant_type,
            data.get('authorization_grant_type')
        )

    def test_post_with_user(self):
        data = {
            'name': 'test app',
            'description': '',
            'download_url': 'http://example.com/download',
            'redirect_uris': 'http://example.com/redirect',
            'authorization_grant_type': 'password'
        }

        view = ApplicationSettings.as_view()
        url = reverse('admin:app_settings', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().post(url, data)
        request.user = UserFactory.create()
        response = view(request, app_id=self.app.id).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'You are not the owner of this application and therefore not '
            'allowed to access this app.'
        )

        ref = Application.objects.get(pk=self.app.id)
        self.assertNotEqual(ref.name, data.get('name'))
        self.assertNotEqual(ref.description, data.get('description'))
        self.assertNotEqual(ref.download_url, data.get('download_url'))
        self.assertNotEqual(ref.redirect_uris, data.get('redirect_uris'))
        self.assertNotEqual(
            ref.authorization_grant_type,
            data.get('authorization_grant_type')
        )

    def test_post_with_anonymous(self):
        data = {
            'name': 'test app',
            'description': '',
            'download_url': 'http://example.com/download',
            'redirect_uris': 'http://example.com/redirect',
            'authorization_grant_type': 'password'
        }

        view = ApplicationSettings.as_view()
        url = reverse('admin:app_settings', kwargs={'app_id': self.app.id})
        request = APIRequestFactory().post(url, data)
        request.user = AnonymousUser()
        response = view(request, app_id=self.app.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

        ref = Application.objects.get(pk=self.app.id)
        self.assertNotEqual(ref.name, data.get('name'))
        self.assertNotEqual(ref.description, data.get('description'))
        self.assertNotEqual(ref.download_url, data.get('download_url'))
        self.assertNotEqual(ref.redirect_uris, data.get('redirect_uris'))
        self.assertNotEqual(
            ref.authorization_grant_type,
            data.get('authorization_grant_type')
        )


class ApplicationDeleteTest(TestCase):
    def setUp(self):
        self.creator = UserFactory.create()
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
        request.user = UserFactory.create()
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
