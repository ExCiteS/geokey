from django.test import TestCase
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from rest_framework.test import APIRequestFactory

from geokey.users.tests.model_factories import UserF

from ..views import SuperuserMixin


class ExampleView(SuperuserMixin, TemplateResponseMixin, View):
    template_name = 'base.html'

    def get(self, request):
        return self.render_to_response({
            'success': 'yes'
        })


class SuperuserMixinTest(TestCase):
    def test_user(self):
        view = ExampleView.as_view()
        request = APIRequestFactory().get('http://example.com')
        request.user = UserF.create()
        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'This extension is for super users only.'
        )

    def test_superuser(self):
        view = ExampleView.as_view()
        request = APIRequestFactory().get('http://example.com')
        request.user = UserF.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'This extension is for super users only.'
        )
