"""Tests for template tags of users."""

from django.test import TestCase

from geokey.categories.tests.model_factories import CategoryFactory

from ..templatetags import filter_tags


class TemplateTagsTest(TestCase):
    def test_show_restrict(self):
        category = CategoryFactory.create()
        self.assertEqual(
            filter_tags.show_restrict({str(category.id): {}}, category),
            '<a href="#" class="text-danger activate-detailed">'
            'Restrict further</a>'
        )
        self.assertEqual(
            filter_tags.show_restrict({'2': {}}, category),
            ''
        )

    def test_is_selected(self):
        dict = ["1", "2", "3"]

        self.assertEqual(filter_tags.is_selected(1, dict), 'selected')
        self.assertEqual(filter_tags.is_selected(4, dict), '')

    def test_is_in(self):
        dict = {
            '1': {},
            '2': {}
        }

        self.assertTrue(filter_tags.is_in(dict, 1))
        self.assertFalse(filter_tags.is_in(dict, 4))

    def test_minval(self):
        self.assertEqual(filter_tags.minval({'minval': 5}), 5)
        self.assertEqual(filter_tags.minval({}), '')

    def test_maxval(self):
        self.assertEqual(filter_tags.maxval({'maxval': 5}), 5)
        self.assertEqual(filter_tags.maxval({}), '')
