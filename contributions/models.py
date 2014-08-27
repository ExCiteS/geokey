from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis
from django.core.exceptions import ValidationError

from django_hstore import hstore
from simple_history.models import HistoricalRecords

from core.exceptions import InputError

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


class Observation(models.Model):
    """
    Stores a single observation.
    """
    location = models.ForeignKey('Location', related_name='locations')
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
    attributes = hstore.DictionaryField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='creator'
    )
    updator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='updator',
        null=True
    )
    version = models.IntegerField(default=1)

    history = HistoricalRecords()
    objects = ObservationManager()

    @classmethod
    def validate_partial(self, observationtype, data):
        """
        Validates the update data of the observation
        """
        is_valid = True
        error_messages = []

        for field in observationtype.fields.all().filter(status='active'):
            if field.key in data and data.get(field.key) is not None:
                try:
                    field.validate_input(data.get(field.key))
                except InputError, error:
                    is_valid = False
                    error_messages.append(error)

        if not is_valid:
            raise ValidationError(error_messages)

    @classmethod
    def validate_full(self, observationtype, data):
        is_valid = True
        error_messages = []

        for field in observationtype.fields.all().filter(status='active'):
            try:
                field.validate_input(data.get(field.key))
            except InputError, error:
                is_valid = False
                error_messages.append(error)

        if not is_valid:
            raise ValidationError(error_messages)

    @classmethod
    def replace_null(self, attributes):
        for key, value in attributes.iteritems():
            if isinstance(value, (str, unicode)) and len(value) == 0:
                attributes[key] = None

        return attributes


    @classmethod
    def create(cls, attributes=None, creator=None, location=None,
               observationtype=None, project=None, status=None):
        """
        Creates a new observation. Validates all fields first and raises a
        ValidationError if at least one field did not validate.
        Creates the object if all fields are valid.
        """
        attributes = cls.replace_null(attributes)

        if status == None:
            status = 'pending'

        if status == 'draft':
            cls.validate_partial(observationtype, attributes)
        else:
            cls.validate_full(observationtype, attributes)

        location.save()
        observation = cls.objects.create(
            location=location,
            observationtype=observationtype,
            project=project,
            attributes=attributes,
            creator=creator,
            status=status
        )
        return observation

    def update(self, attributes, updator, review_comment=None, status=None):
        """
        Updates data of the observation
        """
        update = self.attributes.copy()

        if attributes is not None:
            attributes = self.replace_null(attributes)
            update.update(attributes)

        if status == 'draft' or (status is None and self.status == 'draft'):
            self.validate_partial(self.observationtype, update)
        else:
            self.validate_full(self.observationtype, update)
            self.version = self.version + 1

        self.attributes = update
        self.updator = updator
        self.review_comment = review_comment

        self.status = status or self.status

        self.save()
        return self

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
    commentto = models.ForeignKey('Observation', related_name='comments')
    respondsto = models.ForeignKey('Comment', null=True, blank=True,
                                   related_name='responses')
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
