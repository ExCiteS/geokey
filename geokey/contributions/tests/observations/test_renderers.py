"""Tests for renderers of contributions (observations)."""

import json

from django.test import TestCase
from django.template.loader import render_to_string

from geokey.contributions.renderers.geojson import GeoJsonRenderer
from geokey.contributions.renderers.kml import KmlRenderer


class KmlRendererTest(TestCase):
    def setUp(self):
        self.contrib = {
            'id': 1,
            'location': {
                'id': 1,
                'name': 'Location',
                'description': None,
                'geometry': '{"type": "Point","coordinates": [ '
                            '-0.144415497779846, 51.54671869005856]}'
            },
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            },
            "display_field": {
                "key": "name",
                "value": "The Grafton"
            },
            "meta": {
                "creator": {
                    "id": 2,
                    "display_name": "Oliver"
                },
                "isowner": True,
                "updator": None,
                "status": "active",
                "created_at": "2014-09-19T15:51:32.804Z",
                "updated_at": "2014-09-21T15:51:32.804Z",
                "version": 1,
                "category": {
                    "id": 40,
                    "name": "Pubs",
                    "description": "",
                    "status": "active",
                    "fields": [
                        {
                            "id": 117,
                            "name": "Name",
                            "key": "name",
                            "fieldtype": "TextField",
                            "description": "",
                            "status": "active",
                            "required": True
                        },
                        {
                            "id": 118,
                            "name": "Address",
                            "key": "address",
                            "fieldtype": "TextField",
                            "description": "",
                            "status": "active",
                            "required": False
                        },
                        {
                            "id": 119,
                            "name": "Child friedly",
                            "key": "child_friedly",
                            "fieldtype": "TrueFalseField",
                            "description": "Would your take your kids?",
                            "status": "active",
                            "required": False
                        }
                    ],
                    "colour": "#0033ff",
                    "created_at": "2014-09-17T00:00:00Z"
                }
            },
            "comments": [],
            "review_comments": [],
            "media": []
        }

    def test_render(self):
        renderer = KmlRenderer()
        result = renderer.render([self.contrib])

        rendered = render_to_string(
            'geometries/placemarks.kml',
            {'data': [self.contrib]}
        )
        self.assertEqual(result, rendered)


class GeoJsonRendererTest(TestCase):
    def setUp(self):
        self.contrib = {
            'id': 1,
            'location': {
                'id': 1,
                'name': 'Location',
                'description': None,
                'geometry': '{"type": "Point","coordinates": [ '
                            '-0.144415497779846, 51.54671869005856]}'
            },
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            },
            "meta": {
                "creator": {
                    "id": 2,
                    "display_name": "Oliver"
                },
                "isowner": True,
                "updator": None,
                "status": "active",
                "created_at": "2014-09-19T15:51:32.804Z",
                "updated_at": "2014-09-21T15:51:32.804Z",
                "version": 1,
                "category": {
                    "id": 40,
                    "name": "Pubs",
                    "description": "",
                    "status": "active",
                    "fields": [
                        {
                            "id": 117,
                            "name": "Name",
                            "key": "name",
                            "fieldtype": "TextField",
                            "description": "",
                            "status": "active",
                            "required": True
                        },
                        {
                            "id": 118,
                            "name": "Address",
                            "key": "address",
                            "fieldtype": "TextField",
                            "description": "",
                            "status": "active",
                            "required": False
                        },
                        {
                            "id": 119,
                            "name": "Child friedly",
                            "key": "child_friedly",
                            "fieldtype": "TrueFalseField",
                            "description": "Would your take your kids?",
                            "status": "active",
                            "required": False
                        }
                    ],
                    "colour": "#0033ff",
                    "created_at": "2014-09-17T00:00:00Z"
                }
            },
            "comments": [],
            "review_comments": [],
            "media": []
        }

    def test_render_single(self):
        renderer = GeoJsonRenderer()
        result = renderer.render_single(self.contrib)

        self.assertTrue('geometry' in result)
        self.assertFalse('geometry' in result.get('location'))

    def test_render_many(self):
        renderer = GeoJsonRenderer()
        result = renderer.render_many([self.contrib])

        self.assertEqual(result.get('type'), 'FeatureCollection')
        self.assertEqual(len(result.get('features')), 1)

    def test_render_with_none(self):
        renderer = GeoJsonRenderer()
        result = renderer.render(None)

        self.assertEqual(result, '')

    def test_render_with_single(self):
        renderer = GeoJsonRenderer()
        result = json.loads(renderer.render(self.contrib))

        self.assertTrue('geometry' in result)
        self.assertFalse('geometry' in result.get('location'))

    def test_render_with_many(self):
        renderer = GeoJsonRenderer()
        result = json.loads(renderer.render([self.contrib]))

        self.assertEqual(result.get('type'), 'FeatureCollection')
        self.assertEqual(len(result.get('features')), 1)
