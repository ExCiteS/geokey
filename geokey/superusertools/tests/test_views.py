from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect, HttpRequest, QueryDict
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages import get_messages

from allauth.account.models import EmailAddress

from rest_framework.test import APIRequestFactory, force_authenticate

from geokey import version
from geokey.users.tests.model_factories import UserFactory
from geokey.users.models import User
from geokey.projects.tests.model_factories import ProjectFactory

from ..views import (
    PlatformSettings,
    ProjectsList,
    ManageSuperUsers,
    ManageInactiveUsers,
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
        request.user = UserFactory.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_user(self):
        view = PlatformSettings.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().get(url)
        request.user = UserFactory.create(**{'is_superuser': False})
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
        request.user = UserFactory.create(**{'is_superuser': True})

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
        request.user = UserFactory.create(**{'is_superuser': False})
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
        user = UserFactory.create(**{'is_superuser': True})
        ProjectFactory.create_batch(5, add_admins=[user])
        ProjectFactory.create_batch(5)
        view = ProjectsList()
        context = view.get_context_data()
        self.assertEqual(len(context.get('projects')), 10)

    def test_get_with_superuser(self):
        view = ProjectsList.as_view()
        url = reverse('admin:superuser_projects')
        request = APIRequestFactory().get(url)
        request.user = UserFactory.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_user(self):
        view = ProjectsList.as_view()
        url = reverse('admin:superuser_projects')
        request = APIRequestFactory().get(url)
        request.user = UserFactory.create(**{'is_superuser': False})
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
        UserFactory.create_batch(2, **{'is_superuser': True})
        UserFactory.create_batch(2, **{'is_superuser': False})
        view = ManageSuperUsers()
        context = view.get_context_data()
        self.assertEqual(len(context.get('superusers')), 2)

    def test_get_with_superuser(self):
        view = ManageSuperUsers.as_view()
        url = reverse('admin:superuser_manage_users')
        request = APIRequestFactory().get(url)
        request.user = UserFactory.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_user(self):
        view = ManageSuperUsers.as_view()
        url = reverse('admin:superuser_manage_users')
        request = APIRequestFactory().get(url)
        request.user = UserFactory.create(**{'is_superuser': False})
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


class ManageInactiveUsersTest(TestCase):
    def setUp(self):
        self.view = ManageInactiveUsers.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def create_inactive(self):
        self.inactive_1 = UserFactory.create(**{'is_active': False})
        EmailAddress(
            user=self.inactive_1,
            email=self.inactive_1.email,
            verified=False
        ).save()
        self.inactive_2 = UserFactory.create(**{'is_active': False})
        EmailAddress(
            user=self.inactive_2,
            email=self.inactive_2.email,
            verified=False
        ).save()
        self.inactive_3 = UserFactory.create(**{'is_active': False})
        EmailAddress(
            user=self.inactive_3,
            email=self.inactive_3.email,
            verified=False
        ).save()

    def test_get_with_anonymous(self):
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_anonymous(self):
        self.create_inactive()
        self.request.POST = QueryDict(
            'activate_users=%s&activate_users=%s' % (
                self.inactive_1.id, self.inactive_2.id))
        self.request.method = 'POST'
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(User.objects.filter(is_active=False).count(), 3)

    def test_get_with_user(self):
        user = UserFactory.create()
        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'superusertools/manage_inactiveusers.html',
            {
                'error_description': 'Superuser tools are for superusers only.'
                                     ' You are not a superuser.',
                'error': 'Permission denied.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_user(self):
        user = UserFactory.create()
        self.create_inactive()
        self.request.POST = QueryDict(
            'activate_users=%s&activate_users=%s' % (
                self.inactive_1.id, self.inactive_2.id))
        self.request.method = 'POST'
        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'superusertools/manage_inactiveusers.html',
            {
                'error_description': 'Superuser tools are for superusers only.'
                                     ' You are not a superuser.',
                'error': 'Permission denied.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        self.assertEqual(User.objects.filter(is_active=False).count(), 3)

    def test_get_with_superuser(self):
        user = UserFactory.create(**{'is_superuser': True})
        inactive_users = UserFactory.create_batch(3, **{'is_active': False})

        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'superusertools/manage_inactiveusers.html',
            {
                'inactive_users': inactive_users,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_superuser(self):
        user = UserFactory.create(**{'is_superuser': True})
        self.create_inactive()
        self.request.POST = QueryDict(
            'activate_users=%s&activate_users=%s' % (
                self.inactive_1.id, self.inactive_2.id))
        self.request.method = 'POST'
        self.request.user = user

        response = self.view(self.request).render()

        rendered = render_to_string(
            'superusertools/manage_inactiveusers.html',
            {
                'inactive_users': [self.inactive_3],
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        self.assertEqual(
            User.objects.filter(is_active=False).count(), 1
        )
        self.assertEqual(
            EmailAddress.objects.filter(verified=False).count(), 1
        )


class AddSuperUsersAjaxViewTest(TestCase):
    def test_post_with_superuser(self):
        factory = APIRequestFactory()
        user = UserFactory.create(**{'is_superuser': True})
        user_to_add = UserFactory.create(**{'is_superuser': False})
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
        user = UserFactory.create(**{'is_superuser': False})
        user_to_add = UserFactory.create(**{'is_superuser': False})
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
        user = UserFactory.create(**{'is_superuser': True})
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
        user = UserFactory.create(**{'is_superuser': True})
        user_to_remove = UserFactory.create(**{'is_superuser': True})
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
        user = UserFactory.create(**{'is_superuser': False})
        user_to_remove = UserFactory.create(**{'is_superuser': True})
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
        user = UserFactory.create(**{'is_superuser': True})
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
