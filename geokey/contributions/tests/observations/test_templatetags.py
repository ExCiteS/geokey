"""Tests for template tags of contributions (observations)."""

from django.test import TestCase

from geokey.contributions.templatetags import kml_tags

from geokey.categories.tests.model_factories import CategoryFactory


class TemplateTagsTest(TestCase):
    def test_kml_name(self):
        name = kml_tags.kml_name({'display_field': {'value': 'Awesome pub'}})
        self.assertEqual(name, 'Awesome pub')

    def test_kml_name_when_no_display_field(self):
        name = kml_tags.kml_name(None)
        self.assertEqual(name, '')

    def test_kml_name_when_display_field_is_empty(self):
        name = kml_tags.kml_name({'display_field': {}})
        self.assertEqual(name, '')

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
        CategoryFactory.create()
        data = {
            'properties': {
                'key_1': 1,
                'key_2': 'value'
            },
            'meta': {
                'category': {
                    'id': 1,
                }
            },
            'media': [
                {
                    'file_type': 'ImageFile',
                    'name': 'Image',
                    'description': None,
                    'url': '/media/image.png',
                    'thumbnail_url': '/media/image-thumbnail.png'
                },
                {
                    'file_type': 'VideoFile',
                    'name': 'Video',
                    'description': None,
                    'url': 'https://www.youtube.com/watch?v=LueGR1IpfS0',
                    'thumbnail_url': '/static/img/play.png'
                },
                {
                    'file_type': 'AudioFile',
                    'name': 'Audio',
                    'description': 'New feature - audio support.',
                    'url': '/media/audio.mp4',
                    'thumbnail_url': None
                }
            ],
            'comments': [
                {
                    'text': 'Is it ready yet?',
                    'creator': {
                        'display_name': 'Adam'
                    },
                    'responses': [
                        {
                            'text': 'Yes!',
                            'creator': {
                                'display_name': 'Sarah'
                            },
                            'responses': []
                        }
                    ]
                }
            ]
        }
        description = kml_tags.kml_desc(data)
        self.assertEqual(
            description,
            '<![CDATA[<table><tr><td>key_1</td><td>1</td></tr>'
            '<tr><td>key_2</td><td>value</td></tr></table>'
            '<table><tr><td><strong>Image</strong><br /><a href="/media/image.png"><img src="/media/image-thumbnail.png" /></a></td></tr>'
            '<tr><td><strong>Video</strong><br /><a href="https://www.youtube.com/watch?v=LueGR1IpfS0"><img src="/static/img/play.png" /></a></td></tr>'
            '<tr><td><a href="/media/audio.mp4"><strong>Audio</strong></a><br />New feature - audio support.</td></tr></table>'
            '<table><tr><td><strong>Adam</strong><br />Is it ready yet?'
            '<table><tr><td><strong>Sarah</strong><br />Yes!</td></tr></table></td></tr></table>]]>'
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
