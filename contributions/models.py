from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis
from django.core.exceptions import ValidationError

from django_hstore import hstore

from .base import LOCATION_STATUS, OBSERVATION_STATUS, COMMENT_STATUS
from .manager import LocationManager, ObservationManager, CommentManager


class Location(models.Model):
    """
    Represents a location to which an arbitrary number of observations can be
    attached.
    """
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    geometry = gis.GeometryField(geography=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    version = models.IntegerField(default=1)
    private = models.BooleanField(default=False)
    private_for_project = models.ForeignKey('projects.Project', null=True)
    status = models.CharField(
        choices=LOCATION_STATUS,
        default=LOCATION_STATUS.active,
        max_length=20
    )

    objects = LocationManager()


class ObservationData(models.Model):
    attributes = hstore.DictionaryField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    version = models.IntegerField(default=1)
    observation = models.ForeignKey('Observation', related_name='data')


class Observation(models.Model):
    """
    Stores a single observation.
    """
    status = models.CharField(
        choices=OBSERVATION_STATUS,
        default=OBSERVATION_STATUS.active,
        max_length=20
    )
    location = models.ForeignKey('Location', related_name='observations')
    project = models.ForeignKey(
        'projects.Project', related_name='observations'
    )
    observationtype = models.ForeignKey('observationtypes.ObservationType')

    objects = ObservationManager()

    def _data_is_valid(self, data, observationtype):
        is_valid = True
        for field in observationtype.fields.all():
            if not field.validate_input(data.get(field.key)):
                is_valid = False

        return is_valid

    @classmethod
    def create(cls, data=None, creator=None, location=None,
               observationtype=None, project=None):
        """
        Creates a new observation. Validates all fields first and raises a
        ValidationError if at least one field did not validate.
        Creates the object if all fields are valid.
        """
        observation = cls(
            location=location,
            observationtype=observationtype,
            project=project
        )
        if observation._data_is_valid(data, observationtype):
            observation.save()

            ObservationData.objects.create(
                attributes=data,
                creator=creator,
                observation=observation
            )
            return observation
        else:
            raise ValidationError('One or more fields did not validate. The '
                                  'contribution has not been save to the '
                                  'database')

    @property
    def current_data(self):
        """
        Returns the ObservationData instance with the largest version number,
        i.e. the one that is most current
        """
        return self.data.order_by("-version")[0]

    def update(self, data=None, creator=None):
        if self._data_is_valid(data, self.observationtype):
            version = self.current_data.version + 1
            ObservationData.objects.create(
                attributes=data,
                creator=creator,
                observation=self,
                version=version
            )
        else:
            raise ValidationError('One or more fields did not validate. The '
                                  'contribution has not been save to the '
                                  'database')

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = OBSERVATION_STATUS.deleted
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

    objects = CommentManager()

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = COMMENT_STATUS.deleted
        self.save()
