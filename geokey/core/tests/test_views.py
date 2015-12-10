import json

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from django.http import HttpRequest

from geokey.version import get_version

from geokey.core.views import InfoAPIView


# ############################################################################
#
# PUBLIC API VIEWS
#
# ############################################################################

class InfoAPIViewTest(TestCase):
    def test_url(self):
        self.assertEqual(reverse('api:info_api'), '/api/info/')
        
        resolved = resolve('/api/info/')
        self.assertEqual(resolved.func.func_name, InfoAPIView.__name__)

    def test_get(self):
        view = InfoAPIView.as_view()
        request = HttpRequest()
        request.method = 'GET'
        response = view(request).render()
        
        self.assertEqual(response.status_code, 200)
        
        response_json = json.loads(response.content)
        self.assertEqual(response_json.get('geokey_version'), get_version())
