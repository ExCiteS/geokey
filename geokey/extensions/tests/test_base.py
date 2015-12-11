from django.test import TestCase
from ..base import ExtensionExists, register, deregister, extensions as ext


class RegisterExtensionTest(TestCase):
    def setUp(self):
        register('test_ext', 'Test', True, True, '1.0.0')

    def tearDown(self):
        deregister('test_ext')

    def test(self):
        extension = ext.get('test_ext')
        self.assertEqual(extension.get('ext_id'), 'test_ext')
        self.assertEqual(extension.get('name'), 'Test')
        self.assertEqual(extension.get('index_url'), 'test_ext:index')
        self.assertTrue(extension.get('display_admin'))
        self.assertTrue(extension.get('superuser'))
        self.assertEqual(extension.get('version'), '1.0.0')

    def test_exiting(self):
        self.assertRaises(
            ExtensionExists,
            register,
            'test_ext', 'abc', False, False, '0.0.1')
