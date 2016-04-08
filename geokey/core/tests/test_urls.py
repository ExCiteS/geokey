"""Tests for URLs."""

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from geokey.core.views import InfoAPIView


class UrlsTest(TestCase):
    """Test all URLs."""

    def test_reverse_info(self):
        """Test reverser for info API."""
        self.assertEqual(reverse('api:info'), '/api/info/')

    def test_resolve_subset_list(self):
        """Test resolver for info API."""
        resolved = resolve('/api/info/')
        self.assertEqual(resolved.func.__name__, InfoAPIView.__name__)
