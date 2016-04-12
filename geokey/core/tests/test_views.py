"""Tests for core views."""

import json

from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser

from geokey.version import get_version
from geokey.core.views import InfoAPIView
from geokey.users.tests.model_factories import UserFactory
from geokey.extensions.base import register, deregister


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

    def test_get_with_anonymous(self):
        """Test GET with anonymous user."""
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
        self.assertFalse(self.contains_extension('S', installed_extensions))

    def test_get_with_user(self):
        """Test GET with user."""
        self.request.user = UserFactory.create(**{'is_superuser': False})
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
        self.assertFalse(self.contains_extension('S', installed_extensions))

    def test_get_with_superuser(self):
        """Test GET with superuser."""
        self.request.user = UserFactory.create(**{'is_superuser': True})
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
