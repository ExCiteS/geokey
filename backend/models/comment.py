from django.db import models
from django.conf import settings

from .choice import STATUS_TYPES


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

    class Meta:
        abstract = True
        app_label = 'backend'

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = STATUS_TYPES['DELETED']
        self.save()

    def addResponse(self, response):
        """
        Adds a response to a comment.
        """
        response.commentto = self.commentto
        response.respondsto = self
        response.save()

    def getResponses(self):
        """
        Returns all responses to the comment.
        """
        return self.respondsto_set.exclude(status=STATUS_TYPES['DELETED'])


class FeatureComment(Comment):
    """
    A `Comment` on a `Feature`.
    """
    commentto = models.ForeignKey('backend.Feature')
    respondsto = models.ForeignKey(
        'FeatureComment', null=True, related_name='respondsto_set')

    class Meta:
        app_label = 'backend'


class ObservationComment(Comment):
    """
    A `Comment` on an `Observation`.
    """
    commentto = models.ForeignKey('backend.Observation')
    respondsto = models.ForeignKey(
        'ObservationComment', null=True, related_name='respondsto_set')

    class Meta:
        app_label = 'backend'
