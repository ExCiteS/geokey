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
from geokey.socialinteractions.base import freq_dic, STATUS

import importlib

from .model_factories import (
    SocialInteractionFactory,
    SocialInteractionPullFactory
)
from ..models import SocialInteractionPost, SocialInteractionPull
from ..views import (
    SocialInteractionList,
    SocialInteractionPostCreate,
    SocialInteractionPostSettings,
    SocialInteractionPostDelete,
    SocialInteractionPost,
    SocialInteractionPullCreate,
    SocialInteractionPullDelete,
    SocialInteractionPullSettings
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

        self.view = SocialInteractionPostCreate.as_view()
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
            'socialinteractions/socialinteraction_post_create.html',
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

    #     rendered = render_to_string(
    #         'socialinteractions/socialinteraction_post_create.html',
    #         {
    #             'project': self.project,
    #             'auth_users': [self.socialaccount_2],
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
        self.request.POST = {
            'name': 'My social interaction',
            'description': '',
            'socialaccount': self.socialaccount_2.id
        }
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(0, SocialInteractionPost.objects.count())

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
            'socialinteractions/socialinteraction_post_create.html',
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
        self.assertEqual(0, SocialInteractionPost.objects.count())

    def test_post_with_admin(self):
        """
        Updating with project admin.

        It should create the social interaction and redirect to the social
        interaction page to set the post message.
        """
        self.request.method = 'POST'
        post = QueryDict('socialaccount=%s&text_post=%s&text_link=%s' %
                         (
                             self.socialaccount_2.id,
                             'New contribution created for #project. Check it out here $link$',
                             'http://www.mymapfrontend/$project_id$/$contribution_id$'
                         ))

        self.request.POST = post
        self.request.user = self.admin_user
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(1, SocialInteractionPost.objects.count())
        socialinteraction = SocialInteractionPost.objects.first()
        self.assertEqual(socialinteraction.text_to_post,
                         'New contribution created for #project. Check it out here $link$')
        self.assertEqual(socialinteraction.link, 'http://www.mymapfrontend/$project_id$/$contribution_id$')
        self.assertEqual(socialinteraction.project, self.project)
        self.assertEqual(socialinteraction.creator, self.admin_user)
        self.assertEqual(self.socialaccount_2, socialinteraction.socialaccount)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/admin/projects/%s/socialinteractions/' % (
                self.project.id),
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

        self.assertEqual(0, SocialInteractionPost.objects.count())
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

        self.assertEqual(0, SocialInteractionPost.objects.count())
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
        self.view = SocialInteractionPostSettings.as_view()
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
        self.assertEqual(SocialInteractionPost.objects.count(), 1)

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
            'socialinteractions/socialinteraction_post_settings.html',
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
    #         'socialinteractions/socialinteraction_post_settings.html',
    #         {
    #             'project': self.socialinteraction.project,
    #             'socialinteraction': self.socialinteraction,
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
        reference = SocialInteractionPost.objects.get(pk=self.socialinteraction.id)

        post = QueryDict('socialaccount=%s&text_post=%s&text_link=%s' %
                         (
                             self.socialaccount_3.id,
                             'New contribution created for #project. Check it out here $link$',
                             'http://www.mymapfrontend/$project_id$/$contribution_id$'
                         ))

        self.request.POST = post
        response = self.view(
            self.request,
            project_id=self.socialinteraction.project.id,
            socialinteraction_id=self.socialinteraction.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        reference = SocialInteractionPost.objects.get(pk=self.socialinteraction.id)
        self.assertNotEqual(reference.text_to_post, post['text_post'])
        self.assertNotEqual(reference.link, post['text_link'])
        socialaccount = reference.socialaccount
        self.assertNotEqual(self.socialaccount_3, socialaccount)

    def test_post_with_user(self):
        """
        Updating with normal user.

        It should render the page with an error message.
        """
        self.request.method = 'POST'
        post = QueryDict('socialaccount=%s&text_post=%s&text_link=%s' %
                         (
                             self.socialaccount_3.id,
                             'New contribution created for #project. Check it out here $link$',
                             'http://www.mymapfrontend/$project_id$/$contribution_id$'
                         ))

        self.request.POST = post

        self.request.user = self.regular_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_post_settings.html',
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

        reference = SocialInteractionPost.objects.get(pk=self.socialinteraction.id)
        self.assertNotEqual(reference.text_to_post,
                            'New contribution created for #project. Check it out here $link$')
        self.assertNotEqual(reference.link, 'http://www.mymapfrontend/$project_id$/$contribution_id$')
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
        self.view = SocialInteractionPostDelete.as_view()
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
        self.assertEqual(SocialInteractionPost.objects.count(), 1)

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
        self.assertEqual(SocialInteractionPost.objects.count(), 0)

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
        self.assertEqual(SocialInteractionPost.objects.count(), 1)

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
        self.assertEqual(SocialInteractionPost.objects.count(), 1)


@override_settings(INSTALLED_APPS=install_required_apps())
class SocialInteractionPullCreateTest(TestCase):
    """Test creating a new social interaction pull."""

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

        self.view = SocialInteractionPullCreate.as_view()
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
            'socialinteractions/socialinteraction_pull_create.html',
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

        #     rendered = render_to_string(
        #         'socialinteractions/socialinteraction_pull_create.html',
        #         {
        #             'project': self.project,
        #             'auth_users': [
        #                 self.socialaccount_2,
        #                 self.socialaccount_1
        #             ],
        #             'user': self.admin_user,
        #             'PLATFORM_NAME': get_current_site(self.request).name,
        #             'GEOKEY_VERSION': version.get_version()
        #         }
        #     )
        #     self.assertEqual(response.status_code, 200)
        #     response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        #     # self.assertEqual(response, rendered)


class SocialInteractionPullDeleteTest(TestCase):
    """Test social interaction pull delete view."""

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
        self.si_pull = SocialInteractionPullFactory.create(
            socialaccount=self.socialaccount_1,
            project=self.project,
            creator=self.admin_user
        )

        self.view = SocialInteractionPullDelete.as_view()
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
        self.assertEqual(SocialInteractionPull.objects.count(), 1)

    def test_get_with_user(self):
        """
        Accessing the view with normal user.

        It should render the page with an error message.
        """
        self.request.user = self.regular_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteractionpull_id=self.si_pull.id
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
        self.si_pull.project = self.project
        self.si_pull.creator = self.admin_user
        self.si_pull.save()

        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteractionpull_id=self.si_pull.id
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SocialInteractionPull.objects.count(), 0)

    def test_delete_with_admin_when_project_is_locked(self):
        """
        Accessing the view with project admin when project is locked.
        It should render the page.
        """
        self.project.islocked = True
        self.project.save()
        self.si_pull.project = self.project
        self.si_pull.creator = self.admin_user
        self.si_pull.save()
        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteractionpull_id=self.si_pull.id
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'admin:socialinteraction_list',
                args=(self.project.id,)
            ),
            response['location']
        )
        self.assertEqual(SocialInteractionPull.objects.count(), 1)

    def test_delete_with_admin_when_project_does_not_exit(self):
        """
        Accessing the view with project admin when project does not exist.

        It should render the page with an error message.
        """
        self.si_pull.project = self.project
        self.si_pull.creator = self.admin_user
        self.si_pull.save()
        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=634842156456,
            socialinteractionpull_id=self.si_pull.id
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
        self.assertEqual(SocialInteractionPull.objects.count(), 1)


@override_settings(INSTALLED_APPS=install_required_apps())
class SocialInteractionPullSettingsTest(TestCase):
    """Test social interaction pull settings page."""

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
        self.si_pull = SocialInteractionPullFactory.create(
            socialaccount=self.socialaccount_1,
            project=self.project,
            creator=self.admin_user
        )
        self.view = SocialInteractionPullSettings.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = self.anonymous_user

        self.freq = freq_dic.keys()
        refund_dict = {value: key for key, value in STATUS}
        self.status_types = refund_dict.keys()

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
        self.assertEqual(SocialInteractionPull.objects.count(), 1)

    def test_get_with_user(self):
        """
        Accessing the view with normal user.

        It should render the page with an error message.
        """
        self.request.user = self.regular_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteractionpull_id=self.si_pull.id
        ).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_pull.html',
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
    #     self.si_pull.creator = self.admin_user
    #     self.si_pull.project = self.project
    #     self.request.user = self.si_pull.creator
    #     self.si_pull.save()
    #     response = self.view(
    #         self.request,
    #         project_id=self.project.id,
    #         socialinteractionpull_id=self.si_pull.id
    #     ).render()

    #     socialaccounts_log = SocialAccount.objects.filter(
    #         user=self.admin_user,
    #         provider__in=[id for id, name in registry.as_choices()
    #                       if id in ['twitter', 'facebook']]
    #     )

    #     rendered = render_to_string(
    #         'socialinteractions/socialinteraction_pull.html',
    #         {
    #             'project': self.si_pull.project,
    #             'auth_users': socialaccounts_log,
    #             'socialinteraction_pull': self.si_pull,
    #             'user': self.admin_user,
    #             'status_types': self.status_types,
    #             'freq': self.freq,
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
        post = QueryDict('frequency=%s&text_pull=%s&status_type=%s&socialaccount=%s' % (
            'fortnigthly',
            '#hastag',
            'inactive',
            self.socialaccount_3.id,
        ))

        self.request.POST = post
        response = self.view(
            self.request,
            project_id=self.si_pull.project.id,
            socialinteractionpull_id=self.si_pull.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

        reference = SocialInteractionPull.objects.get(id=self.si_pull.id)
        self.assertNotEqual(reference.frequency, 'fortnigthly')
        self.assertNotEqual(reference.text_to_pull, '#hastag')
        self.assertNotEqual(reference.status, 'inactive')
        socialaccount = reference.socialaccount
        self.assertNotEqual(self.socialaccount_3, socialaccount)

        # def test_post_with_user(self):
        #     """
        #     Updating with normal user.
        #
        #     It should render the page with an error message.
        #     """
        #     self.request.method = 'POST'
        #     post = QueryDict('frequency=%s&text_pull=%s&status_type=%s&socialaccount=%s' % (
        #         'fortnigthly',
        #         '#hastag',
        #         'inactive',
        #         self.socialaccount_3.id,
        #     ))
        #     self.request.POST = post
        #
        #     self.request.user = self.regular_user
        #     response = self.view(
        #         self.request,
        #         project_id=self.si_pull.project.id,
        #         socialinteractionpull_id=self.si_pull.id
        #     ).render()
        #
        #     rendered = render_to_string(
        #         'socialinteractions/socialinteraction_pull.html',
        #         {
        #             'error_description': 'Project matching query does not exist.',
        #             'error': 'Not found.',
        #             'user': self.regular_user,
        #             'PLATFORM_NAME': get_current_site(self.request).name,
        #             'GEOKEY_VERSION': version.get_version()
        #         }
        #     )
        #     self.assertEqual(response.status_code, 200)
        #     self.assertEqual(response.content.decode('utf-8'), rendered)
        #
        #     reference = SocialInteractionPull.objects.get(id=self.si_pull.id)
        #     self.assertEqual(str(reference.frequency), 'fortnigthly')
        #     self.assertEqual(str(reference.status), 'inactive')
        #     self.assertEqual(str(reference.text_to_pull), '#hastag')
        #     socialaccount = reference.socialaccount
        #     self.assertEqual(self.socialaccount_3, socialaccount)

        # def test_post_with_admin(self):
        #     """
        #     Updating with admin user.

        #     It should render the page with an error message.
        #     """
        #     self.request.method = 'POST'
        #     post = QueryDict('frequency=%s&text_pull=%s&status_type=%s&socialaccount=%s' % (
        #         'hourly',
        #         '#hastag',
        #         'inactive',
        #         self.socialaccount_3.id,
        #     ))
        #     self.request.POST = post

        #     socialaccounts_log = SocialAccount.objects.filter(
        #         user=self.admin_user,
        #         provider__in=[id for id, name in registry.as_choices()
        #                       if id in ['twitter', 'facebook']]
        #     )

        #     self.request.user = self.admin_user
        #     response = self.view(
        #         self.request,
        #         project_id=self.si_pull.project.id,
        #         socialinteractionpull_id=self.si_pull.id
        #     ).render()

        #     rendered = render_to_string(
        #         'socialinteractions/socialinteraction_pull.html',
        #         {
        #             'project': self.si_pull.project,
        #             'auth_users': socialaccounts_log,
        #             'socialinteraction_pull': self.si_pull,
        #             'user': self.admin_user,
        #             'status_types': self.status_types,
        #             'freq': self.freq,
        #             'PLATFORM_NAME': get_current_site(self.request).name,
        #             'GEOKEY_VERSION': version.get_version()
        #         }
        #     )
        #     self.assertEqual(response.status_code, 200)
        #     self.assertEqual(response.content.decode('utf-8'), rendered)

        #     reference = SocialInteractionPull.objects.get(id=self.si_pull.id)
        #     self.assertEqual(str(reference.frequency), 'hourly')
        #     self.assertEqual(str(reference.status), 'inactive')
        #     self.assertEqual(str(reference.text_to_pull), '#hastag')
        #     socialaccount = reference.socialaccount
        #     self.assertEqual(self.socialaccount_3, socialaccount)
