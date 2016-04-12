"""Tests for mixins of extensions."""

from django.test import TestCase
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin

from rest_framework.test import APIRequestFactory

from geokey.users.tests.model_factories import UserFactory
from geokey.extensions.mixins import SuperuserMixin


class ExampleView(SuperuserMixin, TemplateResponseMixin, View):
    """Set up example view."""

    template_name = 'base.html'

    def get(self, request):
        """Set up GET request."""
        return self.render_to_response({
            'country': 'United Kingdom'
        })


class SuperuserMixinTest(TestCase):
    """Test superuser mixin."""

    def setUp(self):
        """Set up test."""
        self.view = ExampleView.as_view()
        self.request = APIRequestFactory().get('http://example.com')

    def test_with_user(self):
        """Test with user."""
        self.request.user = UserFactory.create(**{'is_superuser': False})
        response = self.view(self.request).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'This extension is for superusers only.'
        )

    def test_with_superuser(self):
        """Test with superuser."""
        self.request.user = UserFactory.create(**{'is_superuser': True})
        response = self.view(self.request).render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'This extension is for superusers only.'
        )
