from django.test import TestCase

from nose.tools import raises

from contributions.models import Comment
from ..model_factories import CommentFactory


class CommentTest(TestCase):
    @raises(Comment.DoesNotExist)
    def test_delete_comment(self):
        comment = CommentFactory()
        comment.delete()
        Comment.objects.get(pk=comment.id)
