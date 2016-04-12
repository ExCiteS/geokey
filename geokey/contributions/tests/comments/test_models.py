"""Tests for models of contributions (comments)."""

from django.test import TestCase

from nose.tools import raises

from geokey.contributions.models import Comment, post_save_comment_count_update
from ..model_factories import ObservationFactory, CommentFactory


class TestCommentPostSave(TestCase):
    def test_post_save_comment_count_update(self):
        observation = ObservationFactory()
        CommentFactory.create_batch(5, **{'commentto': observation})
        comment = CommentFactory.create(**{
            'commentto': observation,
            'status': 'deleted'
        })

        post_save_comment_count_update(Comment, instance=comment)
        self.assertEqual(comment.commentto.num_media, 0)
        self.assertEqual(comment.commentto.num_comments, 5)


class CommentTest(TestCase):
    @raises(Comment.DoesNotExist)
    def test_delete_comment(self):
        comment = CommentFactory()
        comment.delete()
        Comment.objects.get(pk=comment.id)

    def test_delete_nested(self):
        comment = CommentFactory()
        response = CommentFactory(**{'respondsto': comment})
        CommentFactory.create_batch(3, **{'respondsto': response})
        self.assertEquals(len(Comment.objects.all()), 5)
        comment.delete()
        self.assertEquals(len(Comment.objects.all()), 0)
