from django.test import TestCase
from ..templatetags import count


class TemplateTagTest(TestCase):
    def test_more_link_text(self):
        self.assertEqual(
            count.more_link_text(6, 'category', 'categories'),
            'Show 1 more category'
        )

        self.assertEqual(
            count.more_link_text(7, 'category', 'categories'),
            'Show 2 more categories'
        )

        self.assertEqual(
            count.more_link_text(5, 'category', 'categories', 4),
            'Show 1 more category'
        )

        self.assertEqual(
            count.more_link_text(6, 'category', 'categories', 4),
            'Show 2 more categories'
        )
