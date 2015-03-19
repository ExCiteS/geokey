from django.test import TestCase

from nose.tools import raises

from geokey.contributions.models import Comment
from ..model_factories import CommentFactory


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
