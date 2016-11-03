"""Tests for views of social interactions."""

from django.test import TestCase
from django.http import HttpRequest
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage

from allauth.socialaccount.models import SocialAccount

from geokey import version
from geokey.core.tests.helpers import render_helpers
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from .model_factories import SocialInteractionFactory
from ..models import SocialInteraction
from ..views import (
    SocialInteractionList,
    SocialInteractionCreate,
    SocialInteractionSettings,
    SocialInteractionDelete,
)


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


class SocialInteractionCreateTest(TestCase):
    """Test creating a new social interaction."""

    def setUp(self):
        """Set up tests."""
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory.create()
        self.admin_user = UserFactory.create()

        self.project = ProjectFactory.create(creator=self.admin_user)
        self.socialaccount_1 = SocialAccount.objects.create(
            user=self.regular_user, provider='facebook', uid='1')
        self.socialaccount_2 = SocialAccount.objects.create(
            user=self.admin_user, provider='facebook', uid='2')
        self.socialaccount_3 = SocialAccount.objects.create(
            user=self.admin_user, provider='google', uid='3')

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

    def test_get_with_admin(self):
        """
        Accessing the view with project admin.

        It should render the page.
        """
        self.request.user = self.admin_user
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_create.html',
            {
                'project': self.project,
                'auth_users': [self.socialaccount_2],
                'user': self.admin_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

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
        self.request.POST = {
            'name': 'My social interaction',
            'description': '',
            'socialaccount': self.socialaccount_2.id
        }

        self.request.user = self.admin_user
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(1, SocialInteraction.objects.count())
        sociainteraction = SocialInteraction.objects.first()
        self.assertEqual(sociainteraction.name, 'My social interaction')
        self.assertEqual(sociainteraction.description, '')
        self.assertEqual(sociainteraction.project, self.project)
        self.assertEqual(sociainteraction.creator, self.admin_user)
        self.assertEqual(sociainteraction.socialaccount, self.socialaccount_2)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/admin/projects/%s/socialinteractions/%s/' % (
                self.project.id, sociainteraction.id),
            response['location']
        )

    def test_post_on_locked_project_with_admin(self):
        """
        Updating with project admin when the project is locked.

        It should redirect to creating a new social interaction page.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'My social interaction',
            'description': '',
            'socialaccount': self.socialaccount_2.id
        }

        self.project.islocked = True
        self.project.save()

        self.request.user = self.admin_user
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(0, SocialInteraction.objects.count())
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/admin/projects/%s/socialinteractions/new/' % (self.project.id),
            response['location']
        )

    def test_post_when_social_account_does_not_exist_with_admin(self):
        """
        Updating with project admin when the social account is not found.

        It should redirect to creating a new social interaction page.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'My social interaction',
            'description': '',
            'socialaccount': 15615444515
        }

        self.request.user = self.admin_user
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(0, SocialInteraction.objects.count())
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/admin/projects/%s/socialinteractions/new/' % (self.project.id),
            response['location']
        )


class SocialInteractionSettingsTest(TestCase):
    """Test social interaction settings page."""

    def setUp(self):
        """Set up tests."""
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory.create()
        self.admin_user = UserFactory.create()

        self.project = ProjectFactory.create(creator=self.admin_user)

        self.socialaccount = SocialAccount.objects.create(
            user=self.admin_user, provider='facebook', uid='2')

        self.socialinteraction = SocialInteractionFactory(
            project=self.project,
            name='My social interaction',
            description="",
            creator=self.admin_user,
            socialaccount=self.socialaccount
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

    def test_get_with_admin(self):
        """
        Accessing the view with project admin.

        It should render the page.
        """
        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        rendered = render_to_string(
            'socialinteractions/socialinteraction_settings.html',
            {
                'project': self.socialinteraction.project,
                'socialinteraction': self.socialinteraction,
                'user': self.admin_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

    def test_post_with_anonymous(self):
        """
        Updating with AnonymousUser.

        It should redirect to the login page.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'New Name',
            'description': 'New Description',
        }
        response = self.view(
            self.request,
            project_id=self.socialinteraction.project.id,
            socialinteraction_id=self.socialinteraction.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

        reference = SocialInteraction.objects.get(pk=self.socialinteraction.id)
        self.assertNotEqual(reference.name, 'New Name')
        self.assertNotEqual(reference.description, 'New Description')

    def test_post_with_user(self):
        """
        Updating with normal user.

        It should render the page with an error message.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'New Name',
            'description': 'New Description',
        }

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

    def test_post_with_admin(self):
        """
        Updating with project admin.

        It should render the page with a success message.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'New Name',
            'description': 'New Description',
        }

        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=self.socialinteraction.id
        ).render()

        reference = SocialInteraction.objects.get(pk=self.socialinteraction.id)
        self.assertEqual(reference.name, 'New Name')
        self.assertEqual(reference.description, 'New Description')

        rendered = render_to_string(
            'socialinteractions/socialinteraction_settings.html',
            {
                'project': reference.project,
                'socialinteraction': reference,
                'user': self.admin_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

    def test_post_with_admin_when_project_does_not_exist(self):
        """
        Updating with project admin when project does not exist.

        It should render the page with an error message.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'New Name',
            'description': 'New Description',
        }

        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=181651545615,
            socialinteraction_id=self.socialinteraction.id
        )

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'The project is not found.',
                'error': 'Not found.',
                'user': self.admin_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_admin_when_social_interaction_does_not_exist(self):
        """
        Updating with project admin when social int. does not exist.

        It should render the page with an error message.
        """
        self.request.method = 'POST'
        self.request.POST = {
            'name': 'New Name',
            'description': 'New Description',
        }

        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=181651545615
        )

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'The social interaction is not found.',
                'error': 'Not found.',
                'user': self.admin_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


class SocialInteractionDeleteTest(TestCase):
    """Test deleting a social interaction."""

    def setUp(self):
        """Set up tests."""
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory.create()
        self.admin_user = UserFactory.create()

        self.project = ProjectFactory.create(creator=self.admin_user)
        self.socialaccount = SocialAccount.objects.create(
            user=self.admin_user, provider='facebook', uid='1')
        self.socialinteraction = SocialInteractionFactory(
            project=self.project,
            name='My social interaction',
            description="",
            creator=self.admin_user,
            socialaccount=self.socialaccount
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
                args=(self.project.id)
            ),
            response['location']
        )
        self.assertEqual(SocialInteraction.objects.count(), 0)

    def test_delete_with_admin_when_project_is_loked(self):
        """
        Accessing the view with project admin when project is locked.

        It should render the page.
        """
        self.project.islocked = True
        self.project.save()

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
                args=(self.project.id)
            ),
            response['location']
        )
        self.assertEqual(SocialInteraction.objects.count(), 1)

    def test_delete_with_admin_when_project_does_not_exit(self):
        """
        Accessing the view with project admin when project does not exist.

        It should render the page with an error message.
        """
        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=634842156456,
            socialinteraction_id=self.socialinteraction.id
        )

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'The project is not found.',
                'error': 'Not found.',
                'user': self.admin_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        self.assertEqual(SocialInteraction.objects.count(), 1)

    def test_delete_with_admin_when_socialinteraction_does_not_exit(self):
        """
        Accessing the view with project admin when social int. does not exist.

        It should render the page with an error message.
        """
        self.request.user = self.admin_user
        response = self.view(
            self.request,
            project_id=self.project.id,
            socialinteraction_id=634842156456
        )

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'The social interaction is not found.',
                'error': 'Not found.',
                'user': self.admin_user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
        self.assertEqual(SocialInteraction.objects.count(), 1)
