from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site

from rest_framework.test import APIRequestFactory, force_authenticate

from geokey.users.tests.model_factories import UserF
from geokey.users.models import User
from geokey.projects.tests.model_factories import ProjectF

from ..views import (
    PlatformSettings,
    ProjectsList,
    ManageSuperUsers,
    AddSuperUsersAjaxView,
    DeleteSuperUsersAjaxView
)


class SiteSettingsTest(TestCase):
    def test_get_context_data(self):
        view = PlatformSettings()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().get(url)
        view.request = request
        context = view.get_context_data()
        self.assertIsNotNone(context.get('site'))

    def test_get_with_superuser(self):
        view = PlatformSettings.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_user(self):
        view = PlatformSettings.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': False})
        view.request = request
        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Superuser tools are for superusers only. You are not a superuser.'
        )

    def test_get_with_anonymous(self):
        view = PlatformSettings.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        view.request = request
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_post_with_superuser(self):
        data = {
            'name': 'New Name',
            'domain': 'http://domain'
        }
        view = PlatformSettings.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().post(url, data)
        request.user = UserF.create(**{'is_superuser': True})

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request).render()
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response, 'The platform settings have been updated.')

        site = Site.objects.get(pk=1)
        self.assertEqual(site.name, data.get('name'))
        self.assertEqual(site.domain, data.get('domain'))

    def test_post_with_user(self):
        data = {
            'name': 'New Name',
            'domain': 'http://domain'
        }
        view = PlatformSettings.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().post(url, data)
        request.user = UserF.create(**{'is_superuser': False})
        view.request = request
        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Superuser tools are for superusers only. You are not a superuser.'
        )

    def test_post_with_anonymous(self):
        data = {
            'name': 'New Name',
            'domain': 'http://domain'
        }
        view = PlatformSettings.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().post(url, data)
        request.user = AnonymousUser()
        view.request = request
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class ProjectsListTest(TestCase):
    def test_get_context_data(self):
        user = UserF.create(**{'is_superuser': True})
        ProjectF.create_batch(5, add_admins=[user])
        ProjectF.create_batch(5)
        view = ProjectsList()
        context = view.get_context_data()
        self.assertEqual(len(context.get('projects')), 10)

    def test_get_with_superuser(self):
        view = ProjectsList.as_view()
        url = reverse('admin:superuser_projects')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_user(self):
        view = ProjectsList.as_view()
        url = reverse('admin:superuser_projects')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': False})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Superuser tools are for superusers only. You are not a superuser.'
        )

    def test_get_with_anonymous(self):
        view = ProjectsList.as_view()
        url = reverse('admin:superuser_projects')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class ManageSuperUsersTest(TestCase):
    def test_get_context_data(self):
        UserF.create_batch(2, **{'is_superuser': True})
        UserF.create_batch(2, **{'is_superuser': False})
        view = ManageSuperUsers()
        context = view.get_context_data()
        self.assertEqual(len(context.get('superusers')), 2)

    def test_get_with_superuser(self):
        view = ManageSuperUsers.as_view()
        url = reverse('admin:superuser_manage_users')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_user(self):
        view = ManageSuperUsers.as_view()
        url = reverse('admin:superuser_manage_users')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': False})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Superuser tools are for superusers only. You are not a superuser.'
        )

    def test_get_with_anonymous(self):
        view = ManageSuperUsers.as_view()
        url = reverse('admin:superuser_manage_users')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class AddSuperUsersAjaxViewTest(TestCase):
    def test_post_with_superuser(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': True})
        user_to_add = UserF.create(**{'is_superuser': False})
        request = factory.post(
            reverse('ajax:superusers_adduser'),
            {'userId': user_to_add.id}
        )
        force_authenticate(request, user=user)
        view = AddSuperUsersAjaxView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 2)

    def test_post_with_user(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': False})
        user_to_add = UserF.create(**{'is_superuser': False})
        request = factory.post(
            reverse('ajax:superusers_adduser'),
            {'userId': user_to_add.id}
        )
        force_authenticate(request, user=user)
        view = AddSuperUsersAjaxView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 0)

    def test_post_non_existing_user(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': True})
        request = factory.post(
            reverse('ajax:superusers_adduser'),
            {'userId': 78463857934859}
        )
        force_authenticate(request, user=user)
        view = AddSuperUsersAjaxView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 1)


class DeleteSuperUsersAjaxViewTest(TestCase):
    def test_delete_with_superuser(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': True})
        user_to_remove = UserF.create(**{'is_superuser': True})
        request = factory.delete(
            reverse('ajax:superusers_deleteuser', kwargs={
                'user_id': user_to_remove.id
            })
        )
        force_authenticate(request, user=user)
        view = DeleteSuperUsersAjaxView.as_view()
        response = view(request, user_id=user_to_remove.id).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 1)

    def test_delete_with_user(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': False})
        user_to_remove = UserF.create(**{'is_superuser': True})
        request = factory.delete(
            reverse('ajax:superusers_deleteuser', kwargs={
                'user_id': user_to_remove.id
            })
        )
        force_authenticate(request, user=user)
        view = DeleteSuperUsersAjaxView.as_view()
        response = view(request, user_id=user_to_remove.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 1)

    def test_delete_not_existing_user(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': True})
        request = factory.delete(
            reverse('ajax:superusers_deleteuser', kwargs={
                'user_id': 84774358734
            })
        )
        force_authenticate(request, user=user)
        view = DeleteSuperUsersAjaxView.as_view()
        response = view(request, user_id=84774358734).render()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 1)
