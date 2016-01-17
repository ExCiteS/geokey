from django.test import TestCase
from ..base import ExtensionExists, register, deregister, extensions


class RegisterExtensionTest(TestCase):
    def test_register_new(self):
        ext_name = 'test_ext_A'
        register(ext_name, 'Test', True, True, '1.0.0')
    
        extension = extensions.get(ext_name)
        self.assertEqual(extension.get('ext_id'), ext_name)
        self.assertEqual(extension.get('name'), 'Test')
        self.assertEqual(extension.get('index_url'), ext_name + ':index')
        self.assertTrue(extension.get('display_admin'))
        self.assertTrue(extension.get('superuser'))
        self.assertEqual(extension.get('version'), '1.0.0')

    def test_register_existing(self):
        register('test_ext_existing', 'Test', True, True, '1.0.0')
        self.assertRaises(
            ExtensionExists,
            register,
            'test_ext_existing', 'abc', False, False, '0.0.1')

    def test_deregister(self):
        ext_name = 'test_ext_B'
        register(ext_name, 'Test', True, True, '1.0.0')
        
        deregister(ext_name)
        
        self.assertNotIn(ext_name, extensions)
