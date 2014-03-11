from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis

from django_hstore import hstore

from .base import LOCATION_STATUS, OBSERVATION_STATUS, COMMENT_STATUS


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
    version = models.IntegerField(default=1)
    # if private is True and private_for_project is not null, the location
    # shall be available for further contributions to the project.
    # if private is False, the location is public to contributors accross all
    # projects if the platform
    private = models.BooleanField(default=False)
    private_for_project = models.ForeignKey('projects.Project', null=True)
    status = models.CharField(
        choices=LOCATION_STATUS,
        default=LOCATION_STATUS.active,
        max_length=20
    )


class Observation(models.Model):
    """
    Stores a single observation.
    """
    data = hstore.DictionaryField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    location = models.ForeignKey('Location', related_name='observations')
    project = models.ForeignKey(
        'projects.Project', related_name='observations'
    )
    version = models.IntegerField(default=1)
    status = models.CharField(
        choices=OBSERVATION_STATUS,
        default=OBSERVATION_STATUS.active,
        max_length=20
    )
    observationtype = models.ForeignKey('observationtypes.ObservationType')

    objects = hstore.HStoreGeoManager()

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = self.CONTRIBUTION_STATUS.deleted
        self.save()


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    commentto = models.ForeignKey('Observation')
    respondsto = models.ForeignKey('Comment', null=True, blank=True)
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
