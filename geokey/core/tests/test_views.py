import json

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser

from geokey.version import get_version
from geokey.users.models import User
from geokey.core.views import InfoAPIView
from geokey.extensions.base import register, deregister


# ############################################################################
#
# PUBLIC API VIEWS
#
# ############################################################################

class InfoAPIViewTest(TestCase):
    def setUp(self):
        # register bogus extensions:
        register('A', 'A', display_admin=True, superuser=False, version='1.0')
        register('B', 'B', display_admin=True, superuser=False)
        register('S', 'S', display_admin=True, superuser=True, version='0.1.0')

    def tearDown(self):
        # deregister bogus extensions:
        deregister('A')
        deregister('B')
        deregister('S')

    def test_url(self):
        self.assertEqual(reverse('api:info_api'), '/api/info/')
        resolved = resolve('/api/info/')
        self.assertEqual(resolved.func.func_name, InfoAPIView.__name__)

    def contains_extension(self, ext_id, exts_json):
        for ext in exts_json:
            if 'name' in ext and ext['name'] == ext_id:
                return True
        return False

    def test_get_with_anonymous(self):
        view = InfoAPIView.as_view()
        request = HttpRequest()
        request.method = 'GET'
        request.user = AnonymousUser()
        response = view(request).render()

        self.assertEqual(response.status_code, 200)
        
        response_json = json.loads(response.content)
        
        self.assertIn('geokey', response_json)
        geokey_json = response_json.get('geokey')
        self.assertEqual(geokey_json.get('version'), get_version())
        self.assertIn('installed_extensions', geokey_json)
        
        exts_json = response_json.get('geokey').get('installed_extensions')
        self.assertTrue(self.contains_extension('A', exts_json))
        self.assertTrue(self.contains_extension('B', exts_json))
        # superuser extension must be hidden:
        self.assertFalse(self.contains_extension('S', exts_json))

    def test_get_with_user(self):
        view = InfoAPIView.as_view()
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user("a@a.com", "test", "test")
        response = view(request).render()

        self.assertEqual(response.status_code, 200)
        
        response_json = json.loads(response.content)
        
        self.assertIn('geokey', response_json)
        geokey_json = response_json.get('geokey')
        self.assertEqual(geokey_json.get('version'), get_version())
        self.assertIn('installed_extensions', geokey_json)
        
        exts_json = response_json.get('geokey').get('installed_extensions')
        self.assertTrue(self.contains_extension('A', exts_json))
        self.assertTrue(self.contains_extension('B', exts_json))
        # superuser extension must be hidden:
        self.assertFalse(self.contains_extension('S', exts_json))

    def test_get_with_superuser(self):
        view = InfoAPIView.as_view()
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_superuser("s@s.com", "test", "test")
        response = view(request).render()

        self.assertEqual(response.status_code, 200)
        
        response_json = json.loads(response.content)
        
        self.assertIn('geokey', response_json)
        geokey_json = response_json.get('geokey')
        self.assertEqual(geokey_json.get('version'), get_version())
        self.assertIn('installed_extensions', geokey_json)
        
        exts_json = response_json.get('geokey').get('installed_extensions')
        self.assertTrue(self.contains_extension('A', exts_json))
        self.assertTrue(self.contains_extension('B', exts_json))
        # superuser extension must be shown:
        self.assertTrue(self.contains_extension('S', exts_json))
