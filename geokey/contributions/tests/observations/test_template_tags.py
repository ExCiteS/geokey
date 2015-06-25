from django.test import TestCase

from geokey.contributions.templatetags import kml_tags as tags


class TemplateTagsTest(TestCase):
    def test_kml_name(self):
        name = tags.kml_name({'display_field': {'value': 'Awesome pub'}})
        self.assertEqual(name, 'Awesome pub')
