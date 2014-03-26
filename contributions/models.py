from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis
from django.core.exceptions import ValidationError

from django_hstore import hstore

from core.exceptions import InputError, MalformedRequestData

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
    location = models.ForeignKey('Location', related_name='observations')
    project = models.ForeignKey(
        'projects.Project', related_name='observations'
    )
    observationtype = models.ForeignKey('observationtypes.ObservationType')
    status = models.CharField(
        choices=OBSERVATION_STATUS,
        default=OBSERVATION_STATUS.active,
        max_length=20
    )
    review_comment = models.TextField(blank=True, null=True)
    conflict_version = models.IntegerField(blank=True, null=True)

    objects = ObservationManager()

    @classmethod
    def create(cls, data=None, creator=None, location=None,
               observationtype=None, project=None):
        """
        Creates a new observation. Validates all fields first and raises a
        ValidationError if at least one field did not validate.
        Creates the object if all fields are valid.
        """
        is_valid = True
        error_messages = []
        for field in observationtype.fields.all():
            try:
                field.validate_input(data.get(field.key))
            except InputError, error:
                is_valid = False
                error_messages.append(error)

        if is_valid:
            observation = cls(
                location=location,
                observationtype=observationtype,
                project=project
            )
            observation.save()

            ObservationData.objects.create(
                attributes=data,
                creator=creator,
                observation=observation
            )
            return observation
        else:
            raise ValidationError(error_messages)

    @property
    def current_data(self):
        """
        Returns the ObservationData instance with the largest version number,
        i.e. the one that is most current
        """
        return self.data.order_by('-version')[0]

    def validate_update(self, data):
        is_valid = True
        error_messages = []

        for field in self.observationtype.fields.all():
            if field.key in data:
                try:
                    field.validate_input(data.get(field.key))
                except InputError, error:
                    is_valid = False
                    error_messages.append(error)

        if not is_valid:
            raise ValidationError(error_messages)

    def update(self, data=None, creator=None):
        self.validate_update(data)

        try:
            version_on_client = data.pop('version')
        except KeyError:
            raise MalformedRequestData('You must provide the current '
                                       'version number of the observation.'
                                       ' The observation has not been '
                                       'updated.')

        version_in_database = self.current_data.version

        if version_on_client > version_in_database:
            raise MalformedRequestData('The version number you provided '
                                       'for the observation does not '
                                       'exist.')
        else:
            if version_on_client == version_in_database:
                version = version_in_database + 1

            elif version_on_client < version_in_database:
                version = version_in_database

                self.status = 'review'
                self.review_comment = ('Conflicting updates in version '
                                       '%s' % version)
                self.conflict_version = version
                self.save()

            ObservationData.objects.create(
                attributes=data,
                creator=creator,
                observation=self,
                version=version
            )

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
