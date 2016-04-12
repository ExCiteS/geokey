"""Tests for parsers of contributions (observations)."""

import json
from io import BytesIO

from django.test import TestCase

from geokey.contributions.parsers.geojson import GeoJsonParser


class GeoJsonParserTest(TestCase):
    def test_parse_new_contribution_with_existing_location(self):
        obj = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.144415497779846,
                    51.54671869005856
                ]
            },
            "location": {
                "id": 1
            },
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            },
            "meta": {
                "category": 40,
                "status": "active"
            }
        }

        ref = {
            "id": None,
            "location": {
                "id": 1,
                "geometry": '{"type": "Point","coordinates": [ '
                            '-0.144415497779846, 51.54671869005856]}',
            },
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            },
            "meta": {
                "category": 40,
                "status": "active"
            }
        }
        parser = GeoJsonParser()
        parsed = parser.parse(BytesIO(json.dumps(obj)))

        self.assertFalse('id' in parsed)
        self.assertEqual(parsed.get('meta'), ref.get('meta'))
        self.assertEqual(
            parsed.get('location').get('id'),
            ref.get('location').get('id')
        )
        self.assertFalse('name' in parsed.get('location'))
        self.assertFalse('description' in parsed.get('location'))
        self.assertEqual(parsed.get('properties'), ref.get('properties'))

    def test_parse_new_contribution_with_new_empty_location(self):
        obj = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.144415497779846,
                    51.54671869005856
                ]
            },
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            },
            "meta": {
                "category": 40,
                "status": "active"
            }
        }

        ref = {
            "id": None,
            "location": {
                "geometry": '{"type": "Point","coordinates": [ '
                            '-0.144415497779846, 51.54671869005856]}',
            },
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            },
            "meta": {
                "category": 40,
                "status": "active"
            }
        }
        parser = GeoJsonParser()
        parsed = parser.parse(BytesIO(json.dumps(obj)))

        self.assertFalse('id' in parsed)
        self.assertEqual(parsed.get('meta'), ref.get('meta'))
        self.assertFalse('id' in parsed.get('location'))
        self.assertFalse('name' in parsed.get('location'))
        self.assertFalse('description' in parsed.get('location'))
        self.assertEqual(parsed.get('properties'), ref.get('properties'))

    def test_parse_new_contribution_with_new_full_location(self):
        obj = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.144415497779846,
                    51.54671869005856
                ]
            },
            "location": {
                "name": "Location",
                "description": "Location description",
            },
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            },
            "meta": {
                "category": 40,
                "status": "active"
            }
        }

        ref = {
            "id": None,
            "location": {
                "name": "Location",
                "description": "Location description",
                "geometry": '{"type": "Point","coordinates": [ '
                            '-0.144415497779846, 51.54671869005856]}',
            },
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            },
            "meta": {
                "category": 40,
                "status": "active"
            }
        }
        parser = GeoJsonParser()
        parsed = parser.parse(BytesIO(json.dumps(obj)))

        self.assertFalse('id' in parsed)
        self.assertEqual(parsed.get('meta'), ref.get('meta'))
        self.assertEqual(
            parsed.get('location').get('id'),
            ref.get('location').get('id')
        )
        self.assertEqual(
            parsed.get('location').get('name'),
            ref.get('location').get('name')
        )
        self.assertEqual(
            parsed.get('location').get('description'),
            ref.get('location').get('description')
        )
        self.assertEqual(parsed.get('properties'), ref.get('properties'))

    def test_parse_update_properties_only(self):
        obj = {
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            }
        }

        ref = {
            "properties": {
                "child_friendly": False,
                "name": "The Grafton",
                "address": "20 Prince of Wales Rd, London NW5 3LG"
            }
        }
        parser = GeoJsonParser()
        parsed = parser.parse(BytesIO(json.dumps(obj)))

        self.assertFalse('meta' in parsed)
        self.assertFalse('location' in parsed)
        self.assertEqual(parsed.get('properties'), ref.get('properties'))

    def test_parse_update_status_only(self):
        obj = {
            "id": 12,
            "meta": {
                "status": "review"
            }
        }

        parser = GeoJsonParser()
        parsed = parser.parse(BytesIO(json.dumps(obj)))

        self.assertEqual(parsed.get('id'), 12)
        self.assertEqual('review', parsed.get('meta').get('status'))
        self.assertFalse('location' in parsed)
        self.assertFalse('properties' in parsed)

    def test_parse_update_location_only(self):
        obj = {
            "location": {
                "id": 1,
                "name": "Location",
                "description": "Location description"
            }
        }

        parser = GeoJsonParser()
        parsed = parser.parse(BytesIO(json.dumps(obj)))

        self.assertFalse('id' in parsed)
        self.assertFalse('meta' in parsed)
        self.assertEqual(1, parsed.get('location').get('id'))
        self.assertEqual("Location", parsed.get('location').get('name'))
        self.assertEqual(
            "Location description",
            parsed.get('location').get('description')
        )
        self.assertFalse('properties' in parsed)

    def test_parse_update_geometry_only(self):
        obj = {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.144415497779846,
                    51.54671869005856
                ]
            },
        }

        parser = GeoJsonParser()
        parsed = parser.parse(BytesIO(json.dumps(obj)))

        self.assertFalse('id' in parsed)
        self.assertFalse('meta' in parsed)
        self.assertFalse('id' in parsed.get('location'))
        self.assertFalse('name' in parsed.get('location'))
        self.assertFalse('description' in parsed.get('location'))
        self.assertEqual(
            parsed.get('location').get('geometry'),
            '{"type": "Point", "coordinates": ['
            '-0.144415497779846, 51.54671869005856]}'
        )
        self.assertFalse('properties' in parsed)
