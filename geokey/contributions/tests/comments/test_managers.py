"""Tests for managers of contributions (comments)."""

from django.test import TestCase

from ..model_factories import ObservationFactory, CommentFactory
from geokey.contributions.models import Comment


class CommentTest(TestCase):
    def test_get_comments(self):
        observation = ObservationFactory.create()
        CommentFactory.create_batch(5, **{'commentto': observation})
        CommentFactory.create(**{
            'commentto': observation,
            'status': 'deleted'
        })
        comments = Comment.objects.all()
        self.assertEqual(len(comments), 5)
        for comment in comments:
            self.assertNotEqual(comment.status, 'deleted')
