from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis

from djorm_hstore.fields import DictionaryField
from model_utils import Choices

CONTRIBUTION_STATUS = Choices('active', 'inactive', 'review', 'deleted')


class Location(models.Model):
    """
    Represents a location to which an arbitrary number of observations can be
    attached.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    geometry = gis.GeometryField(geography=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.CharField(
        choices=CONTRIBUTION_STATUS,
        default=CONTRIBUTION_STATUS.active,
        max_length=20
    )
    projects = models.ManyToManyField('projects.Project')

    def delete(self):
        """
        Deletes a layer by setting its status to deleted.
        """
        self.status = CONTRIBUTION_STATUS.deleted
        self.save()


class Observation(models.Model):
    """
    Stores a single observation.
    """
    data = DictionaryField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    feature = models.ForeignKey('Location')
    status = models.CharField(
        choices=CONTRIBUTION_STATUS,
        default=CONTRIBUTION_STATUS.active,
        max_length=20
    )
    observationtype = models.ForeignKey('observationtypes.ObservationType')

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = self.CONTRIBUTION_STATUS.deleted
        self.save()


class Comment(models.Model):
    COMMENT_STATUS = Choices('active', 'deleted')

    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    commentto = models.ForeignKey('Observation')
    respondsto = models.ForeignKey('Comment', null=True)
    status = models.CharField(
        choices=COMMENT_STATUS,
        default=COMMENT_STATUS.active,
        max_length=20
    )

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = self.COMMENT_STATUS.deleted
        self.save()
