"""Tests for base of extensions."""

from django.test import TestCase

from geokey.extensions.base import extensions, register, deregister
from geokey.extensions.exceptions import ExtensionExists


class RegisterTest(TestCase):
    """Test register."""

    def tearDown(self):
        """Tear down test."""
        deregister(self.ext_id)

    def test_register(self):
        """Test registering new extension."""
        self.ext_id = 'test_ext'
        register(self.ext_id, 'Test', True, True, '1.0.0')

        extension = extensions.get(self.ext_id)
        self.assertEqual(extension.get('ext_id'), self.ext_id)
        self.assertEqual(extension.get('name'), 'Test')
        self.assertEqual(extension.get('version'), '1.0.0')
        self.assertTrue(extension.get('display_admin'))
        self.assertTrue(extension.get('superuser'))
        self.assertEqual(extension.get('index_url'), self.ext_id + ':index')

    def test_register_when_already_exists(self):
        """Test registering existing extension."""
        self.ext_id = 'test_ext'
        extensions[self.ext_id] = {
            'ext_id': self.ext_id,
            'name': 'Test',
            'version': '1.0.0',
            'display_admin': True,
            'superuser': True,
            'index_url': self.ext_id + ':index'
        }

        with self.assertRaises(ExtensionExists):
            register(self.ext_id, 'Test B', False, False, '1.0.0')


class DeregisterTest(TestCase):
    """Test deregister."""

    def test_deregister(self):
        """Test deregistering existing extension."""
        ext_id = 'test_ext'
        extensions[ext_id] = {
            'ext_id': ext_id,
            'name': 'Test',
            'version': '1.0.0',
            'display_admin': True,
            'superuser': True,
            'index_url': ext_id + ':index'
        }
        deregister(ext_id)

        self.assertNotIn(ext_id, extensions)
