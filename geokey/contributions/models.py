"""Models for contributions."""

import re

from pytz import utc
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.gis.db import models as gis

from django_pgjson.fields import JsonBField
from simple_history.models import HistoricalRecords

from geokey.core.exceptions import InputError

from .base import (
    OBSERVATION_STATUS,
    COMMENT_STATUS,
    COMMENT_REVIEW,
    LOCATION_STATUS,
    MEDIA_STATUS
)
from .managers import (
    ObservationManager,
    LocationManager,
    CommentManager,
    MediaFileManager
)


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
    location = models.ForeignKey(
        Location, related_name='locations'
    )
    project = models.ForeignKey(
        'projects.Project', related_name='observations'
    )
    category = models.ForeignKey('categories.Category')
    status = models.CharField(
        choices=OBSERVATION_STATUS,
        default=OBSERVATION_STATUS.active,
        max_length=20
    )
    properties = JsonBField(default={})
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='creator'
    )
    updated_at = models.DateTimeField(null=True, auto_now_add=True)
    updator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='updator',
        null=True
    )
    version = models.IntegerField(default=1)
    search_index = models.TextField(null=True, blank=True)
    display_field = models.TextField(null=True, blank=True)
    num_media = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)

    history = HistoricalRecords()
    objects = ObservationManager()

    class Meta:
        ordering = ['-updated_at', 'id']

    @classmethod
    def validate_partial(cls, category, data):
        """
        Validates the data against the category field definition. This is a
        partial validation, which is used to validate drafts, field values
        that are not provided are not validated.

        Parameter
        ---------
        category : geokey.categories.models.Category
            Category that the data is validated against
        data : dict
            Dictionary of key-value-pairs; incoming data that is validated

        Raises
        ------
        ValidationError:
            when data is invalid
        """
        is_valid = True
        error_messages = []

        for field in category.fields.all().filter(status='active'):
            if field.key in data and data.get(field.key) is not None:
                try:
                    field.validate_input(data.get(field.key))
                except InputError, error:
                    is_valid = False
                    error_messages.append(error)

        if not is_valid:
            raise ValidationError(error_messages)

    @classmethod
    def validate_full(cls, category, data):
        """
        Validates the data against the category field definition. This is a
        full validation.

        Parameter
        ---------
        category : geokey.categories.models.Category
            Category that the data is validated against
        data : dict
            Dictionary of key-value-pairs; incoming data that is validated

        Raises
        ------
        ValidationError:
            when data is invalid
        """
        is_valid = True
        error_messages = []

        for field in category.fields.all().filter(status='active'):
            try:
                field.validate_input(data.get(field.key))
            except InputError, error:
                is_valid = False
                error_messages.append(error)

        if not is_valid:
            raise ValidationError(error_messages)

    @classmethod
    def create(cls, properties=None, creator=None, location=None,
               category=None, project=None, status=None):
        """
        Creates and returns a new observation. Validates all fields first and
        raises a ValidationError if at least one field did not validate.
        Creates the object if all fields are valid.

        Parameter
        ---------
        properties : dict
            Attributes of the observation
        creator : geokey.users.models.User
            User who creates the observation
        location : geokey.contributions.models.Location
            Location of the contribution
        category : geokey.categories.models.Category
            Category of the contribution
        project : geokey.projects.models.Project
            Project the contribution is assigned to
        status : str
            Status of the contribution; one of active, review, pending or draft

        Return
        ------
        geokey.contributions.models.Observation
            The observation created
        """
        if not properties:
            properties = {}

        location.save()
        observation = cls.objects.create(
            location=location,
            category=category,
            project=project,
            properties=properties,
            creator=creator,
            status=status
        )
        return observation

    def update(self, properties, updator, status=None):
        """
        Updates data of the observation

        Parameter
        ---------
        properties : dict
            Attributes of the observation
        updator : geokey.users.models.User
            User who creates the observation
        status : str
            Status of the contribution; one of active, review, pending or draft

        Return
        ------
        geokey.contributions.models.Observation
            The updated observation
        """
        if status != 'draft':
            self.version = self.version + 1

        if properties:
            self.properties = properties
        self.updator = updator
        self.status = status or self.status
        self.updated_at = datetime.utcnow().replace(tzinfo=utc)

        self.save()
        return self

    def update_display_field(self):
        """
        Updates the display_field attribute. It uses the display field of the
        contributions category and adds a string line 'key:value' to the
        display field property
        """
        display_field = self.category.display_field
        if display_field is not None:
            value = None
            if self.properties:
                value = self.properties.get(display_field.key)

            self.display_field = '%s:%s' % (display_field.key, value)

    def update_count(self):
        """
        Updates the count of media files attached and comments. Should be
        called each time a file or comment is added/deleted.
        """
        self.num_media = self.files_attached.count()
        self.num_comments = self.comments.count()
        self.save()

    def create_search_index(self):
        search_index = []

        for field in self.category.fields.all():
            value = None
            if self.properties and field.key in self.properties.keys():
                if field.fieldtype == 'TextField':
                    value = self.properties.get(field.key)

                if field.fieldtype == 'NumericField':
                    value = str(self.properties.get(field.key))

                if field.fieldtype == 'LookupField':
                    lookup_id = self.properties.get(field.key)
                    if lookup_id:
                        value = field.lookupvalues.get(pk=lookup_id).name

                if field.fieldtype == 'MultipleLookupField':
                    lookup_id = self.properties.get(field.key)
                    if lookup_id:
                        lookupvalues = field.lookupvalues.filter(
                            pk__in=lookup_id
                        )

                        value = ' '.join([val.name for val in lookupvalues])

            if value:
                cleaned = re.sub(r'[\W_]+', ' ', value)
                terms = cleaned.lower().split()

                search_index = search_index + list(
                    set(terms) - set(search_index)
                )

        self.search_index = ','.join(search_index)

    def delete(self):
        """
        Deletes the observation by setting it's status to DELETED
        """
        self.status = OBSERVATION_STATUS.deleted
        self.save()


@receiver(pre_save, sender=Observation)
def pre_save_observation_update(sender, **kwargs):
    """
    Receiver that is called before an observation is saved. Updates
    search_index and display_field properties.
    """
    observation = kwargs.get('instance')
    observation.update_display_field()
    observation.create_search_index()


class Comment(models.Model):
    """
    A comment that is added to a contribution.
    """
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    commentto = models.ForeignKey('Observation', related_name='comments')
    respondsto = models.ForeignKey(
        'Comment',
        null=True,
        blank=True,
        related_name='responses'
    )
    status = models.CharField(
        choices=COMMENT_STATUS,
        default=COMMENT_STATUS.active,
        max_length=20
    )
    review_status = models.CharField(
        choices=COMMENT_REVIEW,
        null=True,
        blank=True,
        max_length=10
    )

    objects = CommentManager()

    class Meta:
        ordering = ['id']

    def delete(self):
        """
        Deletes the comment by setting it's status to DELETED
        """
        self.responses.all().delete()
        self.status = COMMENT_STATUS.deleted
        self.save()


@receiver(post_save, sender=Comment)
def post_save_comment_count_update(sender, **kwargs):
    """
    Receiver that is called after a comment is saved. Updates num_media and
    num_comments properties.
    """
    comment = kwargs.get('instance')
    comment.commentto.update_count()


class MediaFile(models.Model):
    """
    Base class for all media files. Not to be instaciate; instaciate one of
    the child classes instead.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    contribution = models.ForeignKey(
        'contributions.Observation', related_name='files_attached'
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=MEDIA_STATUS,
        default=MEDIA_STATUS.active,
        max_length=20
    )

    objects = MediaFileManager()

    class Meta:
        ordering = ['id']

    @property
    def type_name(self):
        """
        Returns the type of media file. To be implemented by child classes.

        Raises
        ------
        NotImplementedError
            if called on MediaFile base class
        """
        raise NotImplementedError(
            'The property `type_name` has not been implemented for this '
            'subclass of `MediaFile`.'
        )

    def delete(self):
        """
        Deletes a file by setting its status to deleted
        """
        self.status = MEDIA_STATUS.deleted
        self.save()


class AudioFile(MediaFile):
    """
    Stores audio files uploaded by users.
    """
    audio = models.FileField(upload_to='user-uploads/audio')

    class Meta:
        ordering = ['id']
        app_label = 'contributions'

    @property
    def type_name(self):
        """
        Returns file type name

        Returns
        -------
        str
            'AudioFile'
        """
        return 'AudioFile'


class ImageFile(MediaFile):
    """
    Stores images uploaded by users.
    """
    image = models.ImageField(upload_to='user-uploads/images')

    class Meta:
        ordering = ['id']
        app_label = 'contributions'

    @property
    def type_name(self):
        """
        Returns file type name

        Returns
        -------
        str
            'ImageFile'
        """
        return 'ImageFile'


class VideoFile(MediaFile):
    """
    Stores images uploaded by users.
    """
    video = models.ImageField(upload_to='user-uploads/videos')
    youtube_id = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='user-uploads/videos', null=True)
    youtube_link = models.URLField(max_length=255, null=True, blank=True)
    swf_link = models.URLField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['id']

    @property
    def type_name(self):
        """
        Returns file type name

        Returns
        -------
        str
            'VideoFile'
        """
        return 'VideoFile'


@receiver(post_save)
def post_save_media_file_count_update(sender, **kwargs):
    """
    Receiver that is called after a media file is saved. Updates num_media and
    num_comments properties.
    """
    if sender.__name__ in ['ImageFile', 'VideoFile', 'AudioFile']:
        media_file = kwargs.get('instance')
        media_file.contribution.update_count()
