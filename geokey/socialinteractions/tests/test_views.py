"""Tests for views of social interactions."""

from django.test import TestCase, override_settings
from django.conf import settings
from django.http import HttpRequest, QueryDict
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers import registry

from geokey import version
from geokey.core.tests.helpers import render_helpers
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

import importlib

from .model_factories import SocialInteractionFactory
from ..models import SocialInteraction
from ..views import (
    SocialInteractionList,
    SocialInteractionCreate,
    SocialInteractionSettings,
    SocialInteractionDelete,
)


def install_required_apps():
    """Install Twitter and Facebook providers for django-allauth."""
    installed_apps = settings.INSTALLED_APPS

    apps_to_install = [
        'allauth.socialaccount.providers.twitter',
        'allauth.socialaccount.providers.facebook',
    ]

    for app in apps_to_install:
        if app not in installed_apps:
            installed_apps = installed_apps + (app,)
            importlib.import_module(app + '.provider')

    return installed_apps


class SocialInteractionsListTest(TestCase):
    """Test a list of social interactions page."""

    def setUp(self):
        """Set up tests."""
        self.view = SocialInteractionList.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser.

        It should redirect to the login page.
        """
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Accessing the view with normal user.

        It should render the page with an error message.
        """
        user = UserFactory.create()
        project = ProjectFactory.create()

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_list.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_admin(self):
        """
        Accessing the view with project admin.

        It should render the page.
        """
        project = ProjectFactory.create()
        user = project.creator

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_list.html',
            {
                'project': project,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


@override_settings(INSTALLED_APPS=install_required_apps())
class SocialInteractionCreateTest(TestCase):
    """Test creating a new social interaction."""

    def setUp(self):
        """Set up tests."""
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory.create()
        self.admin_user = UserFactory.create()

        self.project = ProjectFactory.create(creator=self.admin_user)
        self.socialaccount_1 = SocialAccount.objects.create(
            user=self.regular_user, provider='twitter', uid='1')
        self.socialaccount_2 = SocialAccount.objects.create(
            user=self.admin_user, provider='twitter', uid='2')

        self.view = SocialInteractionCreate.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = self.anonymous_user

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser.

        It should redirect to the loginpage.
        """
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Accessing the view with normal user.

        It should render the page with an error message.
        """
        self.request.user = self.regular_user
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_create.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': self.regular_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    # def test_get_with_admin(self):
    #     """
    #     Accessing the view with project admin.

    #     It should render the page.
    #     """
    #     self.request.user = self.admin_user
    #     response = self.view(self.request, project_id=self.project.id).render()

    #     # rendered = render_to_string(
    #     #     'socialinteractions/socialinteraction_create.html',
    #     #     {
    #     #         'project': self.project,
    #     #         'auth_users': [self.socialaccount_2],
    #     #         'user': self.admin_user,
    #     #         'PLATFORM_NAME': get_current_site(self.request).name,
    #     #         'GEOKEY_VERSION': version.get_version()
    #     #     }
    #     # )
    #     self.assertEqual(response.status_code, 200)
    #     response = render_helpers.remove_csrf(response.content.decode('utf-8'))
    #     # self.assertEqual(response, rendered)

    def test_post_with_anonymous(self):
        """
        Updating with AnonymousUser.

        It should redirect to the login page.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'My social interaction',
            'description': '',
            'socialaccount': self.socialaccount_2.id
        }
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(0, SocialInteraction.objects.count())

    def test_post_with_user(self):
        """
        Updating with normal user.

        It should render the page with an error message.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'My social interaction',
            'description': '',
            'socialaccount': self.socialaccount_2.id
        }

        self.request.user = self.regular_user
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_create.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': self.regular_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        self.assertEqual(0, SocialInteraction.objects.count())

    def test_post_with_admin(self):
        """
        Updating with project admin.

        It should create the social interaction and redirect to the social
        interaction settings page.
        """
        self.request.method = 'POST'
        post = QueryDict('name=%s&description=''%s&socialaccount=%s' %
                         (
                          'My social interaction',
                          '',
                          self.socialaccount_2.id
                         ))

        self.request.POST = post

        self.request.user = self.admin_user
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(1, SocialInteraction.objects.count())
        socialinteraction = SocialInteraction.objects.first()
        self.assertEqual(socialinteraction.name, 'My social interaction')
        self.assertEqual(socialinteraction.description, '')
        self.assertEqual(socialinteraction.project, self.project)
        self.assertEqual(socialinteraction.creator, self.admin_user)
        self.assertEqual(self.socialaccount_2, socialinteraction.socialaccount)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/admin/projects/%s/socialinteractions/posts/%s/settings' % (
                self.project.id, socialinteraction.id),
            response['location']
        )

    def test_post_on_locked_project_with_admin(self):
        """
        Updating with project admin when the project is locked.

        It should redirect to creating a new social interaction page.
        """
        self.request.method = 'POST'
        post = QueryDict('name=%s&description=''%s&socialaccount=%s' %
                         (
                          'My social interaction',
                          '',
                          self.socialaccount_2.id
                         ))

        self.request.POST = post
        self.project.islocked = True
        self.project.save()

        self.request.user = self.admin_user
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(0, SocialInteraction.objects.count())
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/admin/projects/%s/socialinteractions/post/create' % (self.project.id),
            response['location']
        )

    def test_post_when_social_accounts_do_not_exist_with_admin(self):
        """
        Updating with project admin when the social account is not found.

        It should redirect to creating a new social interaction page.
        """
        self.request.method = 'POST'
        post = QueryDict('name=%s&description=''%s&socialaccount=%s' %
                         (
                            'My social interaction',
                          '',
                          74746464
                         ))

        self.request.POST = post

        self.request.user = self.admin_user
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(0, SocialInteraction.objects.count())
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/admin/projects/%s/socialinteractions/post/create' % (self.project.id),
            response['location'])


@override_settings(INSTALLED_APPS=install_required_apps())
class SocialInteractionSettingsTest(TestCase):
    """Test social interaction settings page."""

    def setUp(self):
        """Set up tests."""
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory.create()
        self.admin_user = UserFactory.create()

        self.project = ProjectFactory.create(creator=self.admin_user)

        self.socialaccount_2 = SocialAccount.objects.create(
            user=self.admin_user, provider='facebook', uid='2')
        self.socialaccount_1 = SocialAccount.objects.create(
            user=self.admin_user, provider='twitter', uid='1')
        self.socialaccount_3 = SocialAccount.objects.create(
            user=self.admin_user, provider='twitter', uid='3')
        self.socialinteraction = SocialInteractionFactory.create(
            socialaccount=self.socialaccount_1,
            project=self.project,
            creator=self.admin_user
        )
        self.view = SocialInteractionSettings.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = self.anonymous_user

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser.

        It should redirect to the login page.
        """
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(SocialInteraction.objects.count(), 1)

    def test_get_with_user(self):
        """
        Accessing the view with normal user.

        It should render the page with an error message.
        """
        self.request.user = self.regular_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_settings.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': self.regular_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    # def test_get_with_admin(self):
    #     """
    #     Accessing the view with project admin.

    #     It should render the page.
    #     """
    #     socialaccounts_log = SocialAccount.objects.filter(
    #         user=self.admin_user,
    #         provider__in=[id for id, name in registry.as_choices()
    #                       if id in ['twitter', 'facebook']]
    #     )
    #     self.socialinteraction.creator = self.admin_user
    #     self.socialinteraction.project = self.project
    #     self.request.user = self.socialinteraction.creator
    #     self.socialinteraction.save()
    #     response = self.view(
    #         self.request,
    #         project_id=self.project.id,
    #         socialinteraction_id=self.socialinteraction.id
    #     ).render()

    #     socialaccounts_log = SocialAccount.objects.filter(
    #         user=self.admin_user,
    #         provider__in=[id for id, name in registry.as_choices()
    #                       if id in ['twitter', 'facebook']]
    #     )
    #     rendered = render_to_string(
    #         'socialinteractions/socialinteraction_settings.html',
    #         {
    #             'project': self.socialinteraction.project,
    #             'auth_users': socialaccounts_log,
    #             'user': self.admin_user,
    #             'PLATFORM_NAME': get_current_site(self.request).name,
    #             'GEOKEY_VERSION': version.get_version()
    #         }
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     response = render_helpers.remove_csrf(response.content.decode('utf-8'))
    #     self.assertEqual(response, rendered)

    def test_post_with_anonymous(self):
        """
        Updating with AnonymousUser.

        It should redirect to the login page.
        """
        self.request.method = 'POST'
        post = QueryDict('name=%s&description=''%s&socialaccount=%s' % (
            'New Name',
            'New Description',
            self.socialaccount_3.id,
        ))

        self.request.POST = post
        response = self.view(
            self.request,
            project_id=self.socialinteraction.project.id,
            socialinteraction_id=self.socialinteraction.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

        reference = SocialInteraction.objects.get(pk=self.socialinteraction.id)
        self.assertNotEqual(reference.name, 'New Name')
        self.assertNotEqual(reference.description, 'New Description')
        socialaccount = reference.socialaccount
        self.assertNotEqual(self.socialaccount_3, socialaccount)

    def test_post_with_user(self):
        """
        Updating with normal user.

        It should render the page with an error message.
        """
        self.request.method = 'POST'
        post = QueryDict('name=%s&description=''%s&socialaccount=%s' % (
            'New Name',
            'New Description',
            self.socialaccount_3.id,
        ))

        self.request.POST = post

        self.request.user = self.regular_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_settings.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': self.regular_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

        reference = SocialInteraction.objects.get(pk=self.socialinteraction.id)
        self.assertNotEqual(reference.name, 'New Name')
        self.assertNotEqual(reference.description, 'New Description')
        socialaccount = reference.socialaccount
        self.assertNotEqual(self.socialaccount_3, socialaccount)


class SocialInteractionDeleteTest(TestCase):
    """Test social interaction delete view."""

    def setUp(self):
        """Set up test."""
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory.create()
        self.admin_user = UserFactory.create()

        self.project = ProjectFactory.create(creator=self.admin_user)

        self.socialaccount_2 = SocialAccount.objects.create(
            user=self.admin_user, provider='facebook', uid='2')
        self.socialaccount_1 = SocialAccount.objects.create(
            user=self.admin_user, provider='twitter', uid='1')
        self.socialaccount_3 = SocialAccount.objects.create(
            user=self.admin_user, provider='twitter', uid='3')
        self.socialinteraction = SocialInteractionFactory.create(
            socialaccount=self.socialaccount_1,
            project=self.project,
            creator=self.admin_user
        )
        self.view = SocialInteractionDelete.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = self.anonymous_user

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser.

        It should redirect to the login page.
        """
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(SocialInteraction.objects.count(), 1)

    def test_get_with_user(self):
        """
        Accessing the view with normal user.

        It should render the page with an error message.
        """
        self.request.user = self.regular_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': self.regular_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_admin(self):
        """
        Accessing the view with project admin.

        It should render the page.
        """
        self.socialinteraction.project = self.project
        self.socialinteraction.creator = self.admin_user
        self.socialinteraction.save()

        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SocialInteraction.objects.count(), 0)

    def test_delete_with_admin_when_project_is_locked(self):
        """
        Accessing the view with project admin when project is locked.

        It should render the page.
        """
        self.project.islocked = True
        self.project.save()
        self.socialinteraction.project = self.project
        self.socialinteraction.creator = self.admin_user
        self.socialinteraction.save()

        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'admin:socialinteraction_list',
                args=(self.project.id,)
            ),
            response['location']
        )
        self.assertEqual(SocialInteraction.objects.count(), 1)

    def test_delete_with_admin_when_project_does_not_exit(self):
        """
        Accessing the view with project admin when project does not exist.

        It should render the page with an error message.
        """
        self.socialinteraction.project = self.project
        self.socialinteraction.creator = self.admin_user
        self.socialinteraction.save()
        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=634842156456,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': self.admin_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        self.assertEqual(SocialInteraction.objects.count(), 1)


@override_settings(INSTALLED_APPS=install_required_apps())
class SocialInteractionPostTest(TestCase):
    """Test social interaction settings page."""

    def setUp(self):
        """Set up tests."""
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory.create()
        self.admin_user = UserFactory.create()

        self.project = ProjectFactory.create(creator=self.admin_user)

        self.socialaccount_2 = SocialAccount.objects.create(
            user=self.admin_user, provider='facebook', uid='2')
        self.socialaccount_1 = SocialAccount.objects.create(
            user=self.admin_user, provider='twitter', uid='1')
        self.socialaccount_3 = SocialAccount.objects.create(
            user=self.admin_user, provider='twitter', uid='3')
        self.socialinteraction = SocialInteractionFactory.create(
            socialaccount=self.socialaccount_1,
            project=self.project,
            creator=self.admin_user
        )
        self.view = SocialInteractionSettings.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = self.anonymous_user

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser.

        It should redirect to the login page.
        """
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(SocialInteraction.objects.count(), 1)

    def test_get_with_user(self):
        """
        Accessing the view with normal user.

        It should render the page with an error message.
        """
        self.request.user = self.regular_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_post.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': self.regular_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_anonymous(self):
        """
        Updating with AnonymousUser.

        It should redirect to the login page.
        """
        self.request.method = 'POST'
        # post = QueryDict('text_to_post=%s' % (
        #     'text_to_post new new new'
        # ))

        self.request.POST = {
            'text_to_post': 'text_to_post new new new'
        }
        # self.request.POST = post
        response = self.view(
            self.request,
            project_id=self.socialinteraction.project.id,
            socialinteraction_id=self.socialinteraction.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

        reference = SocialInteraction.objects.get(id=self.socialinteraction.id)

        self.assertEqual(reference.name, self.socialinteraction.name)
        self.assertNotEqual(reference.text_to_post, 'text_to_post new new new')
        socialaccount = reference.socialaccount
        self.assertEqual(self.socialaccount_1, socialaccount)

    def test_post_with_user(self):
        """
        Updating with normal user.

        It should render the page with an error message.
        """
        self.request.method = 'POST'
        # self.request.POST = {
        #     'name': 'Name',
        #     'description': 'Description',
        # }
        # post = QueryDict('text_to_post=%s' % (
        #     'text_to_post new new new'
        # ))

        self.request.POST = {
            'text_to_post': 'text_to_post new new new'
        }

        self.request.user = self.regular_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_post.html',
            {
                'error_description': 'Project matching query does not exist.',
                'error': 'Not found.',
                'user': self.regular_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

        reference = SocialInteraction.objects.get(id=self.socialinteraction.id)
        self.assertEqual(reference.name, self.socialinteraction.name)
        self.assertEqual(reference.text_to_post, 'text_to_post new new new')
        socialaccount = reference.socialaccount
        self.assertEqual(self.socialaccount_1, socialaccount)
