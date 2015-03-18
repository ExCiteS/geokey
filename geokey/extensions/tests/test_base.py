from django.test import TestCase
from geokey.extensions.base import ExtensionExists, register, extensions as ext


class RegisterExtensionTest(TestCase):
    def test(self):
        register('text_ext', 'Test', True)
        extension = ext.get('text_ext')
        self.assertEqual(extension.get('ext_id'), 'text_ext')
        self.assertEqual(extension.get('name'), 'Test')
        self.assertEqual(extension.get('index_url'), 'text_ext:index')
        self.assertTrue(extension.get('display_admin'))

    def test_exiting(self):
        ext['text_ext'] = {
            'ext_id': 'text_ext',
            'name': 'Test',
            'display_admin': True,
            'index_url': 'text_ext:index'
        }
        try:
            register('text_ext', 'Test Name', False)
        except ExtensionExists:
            extension = ext.get('text_ext')
            self.assertEqual(extension.get('ext_id'), 'text_ext')
            self.assertEqual(extension.get('name'), 'Test')
            self.assertEqual(
                extension.get('index_url'),
                'text_ext:index'
            )
            self.assertTrue(extension.get('display_admin'))
        else:
            self.fail('ExtensionExists not raised')
