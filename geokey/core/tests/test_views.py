"""Tests for core views."""

import json

from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from geokey.version import get_version
from geokey import version
from geokey.core.views import InfoAPIView, LoggerList
from geokey.extensions.base import register, deregister
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.core.models import LoggerHistory


# ############################################################################
#
# PUBLIC API
#
# ############################################################################

class InfoAPIViewTest(TestCase):
    """Test public API for GeoKey server information."""

    def setUp(self):
        """Set up test."""
        self.view = InfoAPIView.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'

        register('A', 'A', display_admin=True, superuser=False, version='1.0')
        register('B', 'B', display_admin=True, superuser=False)
        register('S', 'S', display_admin=True, superuser=True, version='0.1.0')

    def tearDown(self):
        """Tear down test."""
        deregister('A')
        deregister('B')
        deregister('S')

    def contains_extension(self, ext_id, installed_extensions):
        """Helper to check if extension is in installed extensions."""
        for extension in installed_extensions:
            if 'name' in extension and extension['name'] == ext_id:
                return True

        return False

    def test_get(self):
        """Test GET."""
        self.request.user = AnonymousUser()
        response = self.view(self.request).render()

        self.assertEqual(response.status_code, 200)

        response = json.loads(response.content)
        self.assertIn('geokey', response)

        geokey = response.get('geokey')
        self.assertEqual(geokey.get('version'), get_version())
        self.assertIn('installed_extensions', geokey)

        installed_extensions = geokey.get('installed_extensions')
        self.assertTrue(self.contains_extension('A', installed_extensions))
        self.assertTrue(self.contains_extension('B', installed_extensions))
        self.assertTrue(self.contains_extension('S', installed_extensions))


# ############################################################################
#
# ADMIN PAGES
#
# ############################################################################


class LoggerListTest(TestCase):
    """Test a list of logs page."""

    def setUp(self):
        """Set up tests."""
        self.view = LoggerList.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

        self.project = ProjectFactory.create()

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Accessing the view with AnonymousUser should redirect to the login
        page
        """

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Accessing the view with normal user should render the page with an
        error message
        """

        user = UserFactory.create()
        project = ProjectFactory.create()

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'logger/logger_list.html',
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

        logs = LoggerHistory.objects.filter(
            project__contains={'id': str(project.id)})

        logger_list = LoggerList()

        self.request.user = user
        response = self.view(self.request, project_id=project.id).render()

        rendered = render_to_string(
            'logger/logger_list.html',
            {
                'project': project,
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'logs': logger_list.paginate_logs(
                    logs[::-1],
                    self.request.GET.get('page'))
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
