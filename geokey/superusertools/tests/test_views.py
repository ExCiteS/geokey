"""Tests for views of superuser tools."""

from collections import OrderedDict
from importlib import import_module

from django.test import TestCase
from django.conf import settings
from django.apps import apps
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpRequest, QueryDict
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage

from allauth.account.models import EmailAddress
from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp
from rest_framework.test import APIRequestFactory, force_authenticate

from geokey import version
from geokey.core.tests.helpers import render_helpers
from geokey.users.models import User
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.contributions.tests.model_factories import (
    ObservationFactory,
    CommentFactory
)

from geokey.superusertools.views import (
    ManageSuperusers,
    ManageInactiveUsers,
    ManageProjects,
    PlatformSettings,
    ProviderList,
    ProviderOverview,
    SuperusersAjaxView,
    SingleSuperuserAjaxView
)


# #############################################################################
#
# ADMIN VIEWS
#
# #############################################################################

class ManageSuperusersTest(TestCase):
    """Test manage superusers page."""

    def setUp(self):
        """Set up test."""
        self.url = reverse('admin:superusertools_manage_superusers')
        self.request = APIRequestFactory().get(self.url)

    def test_get_context_data(self):
        """Test getting context data."""
        UserFactory.create_batch(2, **{'is_superuser': True})
        UserFactory.create_batch(2, **{'is_superuser': False})
        view = ManageSuperusers()
        context = view.get_context_data()

        self.assertEqual(len(context.get('superusers')), 2)

    def test_get_with_anonymous(self):
        """Test GET with anonymous user."""
        view = ManageSuperusers.as_view()
        self.request.user = AnonymousUser()
        response = view(self.request)

        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_with_user(self):
        """Test GET with user."""
        view = ManageSuperusers.as_view()
        self.request.user = UserFactory.create(**{'is_superuser': False})
        response = view(self.request).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No rights to access superuser tools.'
        )

    def test_get_with_superuser(self):
        """Test GET with superuser."""
        view = ManageSuperusers.as_view()
        self.request.user = UserFactory.create(**{'is_superuser': True})
        response = view(self.request).render()

        self.assertEqual(response.status_code, 200)


class ManageInactiveUsersTest(TestCase):
    """Test manage inactivate users page."""

    def setUp(self):
        """Set up test."""
        self.view = ManageInactiveUsers.as_view()
        self.request = HttpRequest()

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def create_inactive(self):
        """Create 3 inactive users."""
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
        """Test GET with anonymous user."""
        self.request.method = 'GET'
        self.request.user = AnonymousUser()
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """Test GET with user."""
        user = UserFactory.create(**{'is_superuser': False})
        self.request.method = 'GET'
        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'superusertools/manage_inactive_users.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': user,
                'error': 'Permission denied.',
                'error_description': 'No rights to access superuser tools.',
            }
        )

        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

    def test_get_with_superuser(self):
        """Test GET with superuser."""
        self.create_inactive()
        user = UserFactory.create(**{'is_superuser': True})
        self.request.method = 'GET'
        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'superusertools/manage_inactive_users.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': user,
                'inactive_users': [
                    self.inactive_1,
                    self.inactive_2,
                    self.inactive_3
                ]
            }
        )

        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

    def test_post_with_anonymous(self):
        """Test POST with anonymous user."""
        self.create_inactive()
        self.request.method = 'POST'
        self.request.POST = QueryDict(
            'activate_users=%s&activate_users=%s' % (
                self.inactive_1.id, self.inactive_2.id
            )
        )
        self.request.user = AnonymousUser()
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(User.objects.filter(is_active=False).count(), 3)
        self.assertEqual(len(EmailAddress.objects.filter(verified=False)), 3)

    def test_post_with_user(self):
        """Test POST with user."""
        self.create_inactive()
        user = UserFactory.create()
        self.request.method = 'POST'
        self.request.POST = QueryDict(
            'activate_users=%s&activate_users=%s' % (
                self.inactive_1.id, self.inactive_2.id
            )
        )
        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'superusertools/manage_inactive_users.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': user,
                'error': 'Permission denied.',
                'error_description': 'No rights to access superuser tools.'
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(is_active=False).count(), 3)
        self.assertEqual(len(EmailAddress.objects.filter(verified=False)), 3)

    def test_post_with_superuser(self):
        """Test POST with superuser."""
        self.create_inactive()
        user = UserFactory.create(**{'is_superuser': True})
        self.request.method = 'POST'
        self.request.POST = QueryDict(
            'activate_users=%s&activate_users=%s' % (
                self.inactive_1.id, self.inactive_2.id
            )
        )
        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'superusertools/manage_inactive_users.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': user,
                'messages': get_messages(self.request),
                'inactive_users': [self.inactive_3]
            }
        )

        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)
        self.assertEqual(User.objects.filter(is_active=False).count(), 1)
        self.assertEqual(len(EmailAddress.objects.filter(verified=False)), 1)


class ManageProjectsTest(TestCase):
    """Test manage projects page."""

    def setUp(self):
        """Set up test."""
        self.url = reverse('admin:superusertools_manage_projects')
        self.request = APIRequestFactory().get(self.url)

    def test_get_context_data(self):
        """Test getting context data."""
        user = UserFactory.create(**{'is_superuser': True})

        # 1 contribution, 1 comment
        project_1 = ProjectFactory.create()
        category_1 = CategoryFactory.create(project=project_1)
        contribution_1 = ObservationFactory.create(
            project=project_1,
            category=category_1)
        CommentFactory.create(commentto=contribution_1)

        # 2 contributions (1 deleted), 2 comments
        project_2 = ProjectFactory.create(add_admins=[user])
        category_2 = CategoryFactory.create(project=project_2)
        contribution_2 = ObservationFactory.create(
            project=project_2,
            category=category_2)
        CommentFactory.create(commentto=contribution_2)
        contribution_3 = ObservationFactory.create(
            project=project_2,
            category=category_2)
        CommentFactory.create(commentto=contribution_3)
        contribution_3.delete()

        # 2 contributions (1 deleted), 3 comments (1 deleted)
        project_3 = ProjectFactory.create(add_moderators=[user])
        category_3 = CategoryFactory.create(project=project_3)
        contribution_4 = ObservationFactory.create(
            project=project_3,
            category=category_3)
        CommentFactory.create(commentto=contribution_4)
        comment_to_delete = CommentFactory.create(commentto=contribution_4)
        comment_to_delete.delete()
        contribution_5 = ObservationFactory.create(
            project=project_3,
            category=category_3)
        CommentFactory.create(commentto=contribution_5)
        contribution_5.delete()

        # 1 contribution, 2 comments (1 deleted)
        project_4 = ProjectFactory.create(add_contributors=[user])
        category_4 = CategoryFactory.create(project=project_4)
        contribution_6 = ObservationFactory.create(
            project=project_4,
            category=category_4)
        CommentFactory.create(commentto=contribution_6)
        comment_to_delete = CommentFactory.create(commentto=contribution_6)
        comment_to_delete.delete()

        view = ManageProjects()
        context = view.get_context_data()
        self.assertEqual(len(context.get('projects')), 4)

        for project in context.get('projects'):
            self.assertEqual(project.contributions_count, 1)
            self.assertEqual(project.comments_count, 1)
            self.assertEqual(project.media_count, 0)

    def test_get_with_anonymous(self):
        """Test GET with anonymous user."""
        view = ManageProjects.as_view()
        self.request.user = AnonymousUser()
        response = view(self.request)

        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_with_user(self):
        """Test GET with user."""
        view = ManageProjects.as_view()
        self.request.user = UserFactory.create(**{'is_superuser': False})
        response = view(self.request).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No rights to access superuser tools.'
        )

    def test_get_with_superuser(self):
        """Test GET with superuser."""
        view = ManageProjects.as_view()
        self.request.user = UserFactory.create(**{'is_superuser': True})
        response = view(self.request).render()

        self.assertEqual(response.status_code, 200)


class PlatformSettingsTest(TestCase):
    """Test platform settings page."""

    def setUp(self):
        """Set up test."""
        self.url = reverse('admin:superusertools_platform_settings')

    def test_get_context_data(self):
        """Test getting context data."""
        view = PlatformSettings()
        view.request = APIRequestFactory().get(self.url)
        context = view.get_context_data()

        self.assertIsNotNone(context.get('site'))

    def test_get_with_anonymous(self):
        """Test GET with anonymous user."""
        view = PlatformSettings.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = AnonymousUser()
        view.request = request
        response = view(request)

        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_with_user(self):
        """Test GET with user."""
        view = PlatformSettings.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = UserFactory.create(**{'is_superuser': False})
        view.request = request
        response = view(request).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No rights to access superuser tools.'
        )

    def test_get_with_superuser(self):
        """Test GET with superuser."""
        view = PlatformSettings.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = UserFactory.create(**{'is_superuser': True})
        response = view(request).render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'No rights to access superuser tools.'
        )

    def test_post_with_anonymous(self):
        """Test POST with anonymous user."""
        data = {
            'name': 'New Name',
            'domain': 'http://new-domain.org.uk'
        }
        view = PlatformSettings.as_view()
        request = APIRequestFactory().post(self.url, data)
        request.user = AnonymousUser()
        view.request = request
        response = view(request)

        self.assertTrue(isinstance(response, HttpResponseRedirect))

        reference = Site.objects.latest('id')
        self.assertNotEqual(reference.name, data.get('name'))
        self.assertNotEqual(reference.domain, data.get('domain'))

    def test_post_with_user(self):
        """Test POST with user."""
        data = {
            'name': 'New Name',
            'domain': 'http://new-domain.org.uk'
        }
        view = PlatformSettings.as_view()
        request = APIRequestFactory().post(self.url, data)
        request.user = UserFactory.create(**{'is_superuser': False})
        view.request = request
        response = view(request).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No rights to access superuser tools.'
        )

        reference = Site.objects.latest('id')
        self.assertNotEqual(reference.name, data.get('name'))
        self.assertNotEqual(reference.domain, data.get('domain'))

    def test_post_with_superuser(self):
        """Test POST with superuser."""
        data = {
            'name': 'New Name',
            'domain': 'http://new-domain.org.uk'
        }
        view = PlatformSettings.as_view()
        request = APIRequestFactory().post(self.url, data)
        request.user = UserFactory.create(**{'is_superuser': True})

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Platform settings have been updated.')

        reference = Site.objects.latest('id')
        self.assertEqual(reference.name, data.get('name'))
        self.assertEqual(reference.domain, data.get('domain'))


class ProviderListTest(TestCase):
    """Test a list of all providers page."""

    def setUp(self):
        """Set up test."""
        self.url = reverse('admin:superusertools_provider_list')

    def test_get_context_data(self):
        """Test getting context data."""
        view = ProviderList()
        view.request = APIRequestFactory().get(self.url)
        context = view.get_context_data()

        self.assertIsNotNone(context.get('providers'))

    def test_get_with_anonymous(self):
        """Test GET with anonymous user."""
        view = ProviderList.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = AnonymousUser()
        view.request = request
        response = view(request)

        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_with_user(self):
        """Test GET with user."""
        view = ProviderList.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = UserFactory.create(**{'is_superuser': False})
        view.request = request
        response = view(request).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No rights to access superuser tools.'
        )

    def test_get_with_superuser(self):
        """Test GET with superuser."""
        view = ProviderList.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = UserFactory.create(**{'is_superuser': True})
        view.request = request
        response = view(request).render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'No rights to access superuser tools.'
        )


class ProviderOverviewTest(TestCase):
    """Test overview of a provider page."""

    def setUp(self):
        """Set up test."""
        google_provider = 'allauth.socialaccount.providers.google'
        if google_provider not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS += (google_provider,)
            apps.app_configs = OrderedDict()
            apps.ready = False
            apps.populate(settings.INSTALLED_APPS)
            module = import_module(google_provider + '.provider')
            for cls in getattr(module, 'provider_classes', []):
                providers.registry.register(cls)

        self.url = reverse(
            'admin:superusertools_provider_overview',
            kwargs={'provider_id': 'google'}
        )

    def test_get_context_data_when_social_app_doesnt_exist(self):
        """Test getting context data when social app doesn't exist."""
        view = ProviderOverview()
        view.request = APIRequestFactory().get(self.url)

        social_app = SocialApp.objects.create(
            provider='facebook',
            name='Facebook',
            client_id='xxxxxxxxxxxxxxxxxx',
            secret='xxxxxxxxxxxxxxxxxx',
            key=''
        )
        social_app.sites.add(get_current_site(view.request))

        context = view.get_context_data('google')

        self.assertIsNotNone(context.get('provider'))
        self.assertIsNone(context.get('social_app'))

    def test_get_context_data_when_social_app_exists(self):
        """Test getting context data when social app exists."""
        view = ProviderOverview()
        view.request = APIRequestFactory().get(self.url)

        social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='xxxxxxxxxxxxxxxxxx',
            secret='xxxxxxxxxxxxxxxxxx',
            key=''
        )
        social_app.sites.add(get_current_site(view.request))

        context = view.get_context_data('google')

        self.assertIsNotNone(context.get('provider'))
        self.assertEqual(context.get('social_app'), social_app)

    def test_get_context_data_when_social_app_exists_on_wrong_site(self):
        """Test getting context data when social app exists on wrong site."""
        view = ProviderOverview()
        view.request = APIRequestFactory().get(self.url)

        SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='xxxxxxxxxxxxxxxxxx',
            secret='xxxxxxxxxxxxxxxxxx',
            key=''
        )

        context = view.get_context_data('google')

        self.assertIsNotNone(context.get('provider'))
        self.assertIsNone(context.get('social_app'))

    def test_get_context_data_when_provider_doesnt_exist(self):
        """Test getting context data when provider doesn't exist."""
        url = reverse(
            'admin:superusertools_provider_overview',
            kwargs={'provider_id': 'myawesomeprovider'}
        )
        view = ProviderOverview.as_view()
        request = APIRequestFactory().get(url)
        request.user = UserFactory.create(**{'is_superuser': True})
        view.request = request
        response = view(request, provider_id='myawesomeprovider').render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Provider not found.'
        )

    def test_get_with_anonymous(self):
        """Test GET with anonymous user."""
        view = ProviderOverview.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = AnonymousUser()
        view.request = request
        response = view(request, provider_id='google')

        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_with_user(self):
        """Test GET with user."""
        view = ProviderOverview.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = UserFactory.create(**{'is_superuser': False})
        view.request = request
        response = view(request, provider_id='google').render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No rights to access superuser tools.'
        )

    def test_get_with_superuser(self):
        """Test GET with superuser."""
        view = ProviderOverview.as_view()
        request = APIRequestFactory().get(self.url)
        request.user = UserFactory.create(**{'is_superuser': True})
        view.request = request
        response = view(request, provider_id='google').render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'No rights to access superuser tools.'
        )

    def test_post_with_anonymous(self):
        """Test POST with anonymous user."""
        data = {
            'client_id': 'xxxxxxxxxxxxxxxxxx',
            'secret': 'xxxxxxxxxxxxxxxxxx',
            'key': ''
        }
        view = ProviderOverview.as_view()
        request = APIRequestFactory().post(self.url, data)
        request.user = AnonymousUser()
        view.request = request
        response = view(request, provider_id='google')

        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(SocialApp.objects.count(), 0)

    def test_post_with_user(self):
        """Test POST with user."""
        data = {
            'client_id': 'xxxxxxxxxxxxxxxxxx',
            'secret': 'xxxxxxxxxxxxxxxxxx',
            'key': ''
        }
        view = ProviderOverview.as_view()
        request = APIRequestFactory().post(self.url, data)
        request.user = UserFactory.create(**{'is_superuser': False})
        view.request = request
        response = view(request, provider_id='google').render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No rights to access superuser tools.'
        )
        self.assertEqual(SocialApp.objects.count(), 0)

    def test_post_with_superuser_when_activating(self):
        """Test POST with superuser."""
        data = {
            'client_id': 'xxxxxxxxxxxxxxxxxx',
            'secret': 'xxxxxxxxxxxxxxxxxx',
            'key': ''
        }
        view = ProviderOverview.as_view()
        request = APIRequestFactory().post(self.url, data)
        request.user = UserFactory.create(**{'is_superuser': True})

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request, provider_id='google').render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Provider has been activated.')

        reference = SocialApp.objects.latest('id')
        self.assertEqual(reference.client_id, data.get('client_id'))
        self.assertEqual(reference.secret, data.get('secret'))
        self.assertEqual(reference.key, data.get('key'))

    def test_post_with_superuser_when_updating(self):
        """Test POST with superuser."""
        data = {
            'client_id': 'xxxxxxxxxxxxxxxxxx',
            'secret': 'xxxxxxxxxxxxxxxxxx',
            'key': ''
        }
        view = ProviderOverview.as_view()
        request = APIRequestFactory().post(self.url, data)
        request.user = UserFactory.create(**{'is_superuser': True})

        social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='yyyyyyyyyyyyyyyyyy',
            secret='yyyyyyyyyyyyyyyyyy',
            key=''
        )
        social_app.sites.add(get_current_site(request))

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request, provider_id='google').render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Provider has been updated.')
        self.assertEqual(SocialApp.objects.latest('id'), social_app)

        reference = SocialApp.objects.get(pk=social_app.id)
        self.assertEqual(reference.client_id, data.get('client_id'))
        self.assertEqual(reference.secret, data.get('secret'))
        self.assertEqual(reference.key, data.get('key'))


# #############################################################################
#
# AJAX API
#
# #############################################################################

class SuperusersAjaxViewTest(TestCase):
    """Test Ajax API for all superusers."""

    def setUp(self):
        """Set up test."""
        self.factory = APIRequestFactory()
        self.view = SuperusersAjaxView.as_view()
        self.url = reverse('ajax:superusertools_superusers')

        self.user = UserFactory.create(**{'is_superuser': False})
        self.superuser = UserFactory.create(**{'is_superuser': True})
        self.user_to_add = UserFactory.create(**{'is_superuser': False})

    def test_post_with_anonymous_user(self):
        """Test POST with anonymous user."""
        request = self.factory.post(self.url, {'user_id': self.user_to_add.id})
        response = self.view(request).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)

    def test_post_with_user(self):
        """Test POST with user."""
        request = self.factory.post(self.url, {'user_id': self.user_to_add.id})
        force_authenticate(request, user=self.user)
        response = self.view(request).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)

    def test_post_with_superuser(self):
        """Test POST with superuser."""
        request = self.factory.post(self.url, {'user_id': self.user_to_add.id})
        force_authenticate(request, user=self.superuser)
        response = self.view(request).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 2)

    def test_post_when_no_superuser(self):
        """Test POST with superuser, when user does not exist."""
        request = self.factory.post(self.url, {'user_id': 84774358734})
        force_authenticate(request, user=self.superuser)
        response = self.view(request).render()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)


class SingleSuperuserAjaxViewTest(TestCase):
    """Test Ajax API for a single superuser."""

    def setUp(self):
        """Set up test."""
        self.factory = APIRequestFactory()
        self.view = SingleSuperuserAjaxView.as_view()

        self.user = UserFactory.create(**{'is_superuser': False})
        self.superuser = UserFactory.create(**{'is_superuser': True})
        self.user_to_remove = UserFactory.create(**{'is_superuser': True})

    def test_delete_with_anonymous_user(self):
        """Test DELETE with anonymous user."""
        request = self.factory.delete(
            reverse('ajax:superusertools_single_superuser', kwargs={
                'user_id': self.user_to_remove.id
            })
        )
        response = self.view(request, user_id=self.user_to_remove.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 2)

    def test_delete_with_user(self):
        """Test DELETE with user."""
        request = self.factory.delete(
            reverse('ajax:superusertools_single_superuser', kwargs={
                'user_id': self.user_to_remove.id
            })
        )
        force_authenticate(request, user=self.user)
        response = self.view(request, user_id=self.user_to_remove.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 2)

    def test_delete_with_superuser(self):
        """Test DELETE with superuser."""
        request = self.factory.delete(
            reverse('ajax:superusertools_single_superuser', kwargs={
                'user_id': self.user_to_remove.id
            })
        )
        force_authenticate(request, user=self.superuser)
        response = self.view(request, user_id=self.user_to_remove.id).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)

    def test_delete_when_no_superuser(self):
        """Test DELETE with superuser, when superuser does not exist."""
        request = self.factory.delete(
            reverse('ajax:superusertools_single_superuser', kwargs={
                'user_id': 84774358734
            })
        )
        force_authenticate(request, user=self.superuser)
        response = self.view(request, user_id=84774358734).render()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 2)
