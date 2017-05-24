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

from allauth.compat import importlib

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