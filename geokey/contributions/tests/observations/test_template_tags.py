from django.test import TestCase

from geokey.contributions.templatetags import kml_tags


class TemplateTagsTest(TestCase):
    def test_kml_name(self):
        name = kml_tags.kml_name({'display_field': {'value': 'Awesome pub'}})
        self.assertEqual(name, 'Awesome pub')

    def test_geom(self):
        data = {
            "location": {
                "geometry": {"type": "Point", "coordinates": [-2.812, 51.179]}
            }
        }
        kml_geom = kml_tags.kml_geom(data)
        self.assertEqual(
            kml_geom,
            '<Point><coordinates>-2.812,51.179</coordinates></Point>'
        )

    def test_description(self):
        data = {
            'properties': {
                'key_1': 1,
                'key_2': 'value'
            }
        }
        description = kml_tags.kml_desc(data)
        self.assertEqual(
            description,
            '<![CDATA[<table><tr><td>key_1</td><td>1</td></tr>'
            '<tr><td>key_2</td><td>value</td></tr></table>]]>'
        )

    def test_style(self):
        data = {
            'meta': {
                'category': {
                    'colour': '#ff0000'
                }
            }
        }
        colour = kml_tags.kml_style(data)
        self.assertEqual(colour, 'ff0000')
