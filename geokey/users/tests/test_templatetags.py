from django.test import TestCase

from geokey.categories.tests.model_factories import CategoryFactory

from ..templatetags import tags


class TemplateTagsTest(TestCase):
    def test_show_restrict(self):
        category = CategoryFactory.create()
        self.assertEqual(
            tags.show_restrict({str(category.id): {}}, category),
            '<a href="#" class="text-danger activate-detailed">'
            'Restrict further</a>'
        )
        self.assertEqual(
            tags.show_restrict({'2': {}}, category),
            ''
        )

    def test_is_selected(self):
        dict = ["1", "2", "3"]

        self.assertEqual(tags.is_selected(1, dict), 'selected')
        self.assertEqual(tags.is_selected(4, dict), '')

    def test_is_in(self):
        dict = {
            '1': {},
            '2': {}
        }

        self.assertTrue(tags.is_in(dict, 1))
        self.assertFalse(tags.is_in(dict, 4))

    def test_minval(self):
        self.assertEqual(tags.minval({'minval': 5}), 5)
        self.assertEqual(tags.minval({}), '')

    def test_maxval(self):
        self.assertEqual(tags.maxval({'maxval': 5}), 5)
        self.assertEqual(tags.maxval({}), '')
