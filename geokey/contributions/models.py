from pytz import utc
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save

from django_pgjson.fields import JsonBField
from simple_history.models import HistoricalRecords

from geokey.core.exceptions import InputError

from .base import OBSERVATION_STATUS, COMMENT_STATUS, COMMENT_REVIEW
from .manager import ObservationManager, CommentManager

from django.contrib.gis.db import models as gis

from .base import LOCATION_STATUS
from .manager import LocationManager

from .manager import MediaFileManager
from .base import MEDIA_STATUS


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
    search_matches = models.TextField()
    display_field = models.TextField(null=True, blank=True)

    history = HistoricalRecords()
    objects = ObservationManager()

    class Meta:
        ordering = ['-updated_at', 'id']

    @classmethod
    def validate_partial(self, category, data):
        """
        Validates the update data of the observation
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
    def validate_full(self, category, data):
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
    def replace_null(self, properties):
        for key, value in properties.iteritems():
            if isinstance(value, (str, unicode)) and len(value) == 0:
                properties[key] = None

        return properties

    @classmethod
    def create(cls, properties=None, creator=None, location=None,
               category=None, project=None, status=None):
        """
        Creates a new observation. Validates all fields first and raises a
        ValidationError if at least one field did not validate.
        Creates the object if all fields are valid.
        """
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
        """
        if status != 'draft':
            self.version = self.version + 1

        self.properties = properties
        self.updator = updator
        self.status = status or self.status
        self.updated_at = datetime.utcnow().replace(tzinfo=utc)

        self.save()
        return self

    def update_display_field(self):
        display_field = self.category.display_field
        if display_field is not None:
            value = self.properties.get(display_field.key)
            self.display_field = '%s:%s' % (display_field.key, value)

    def update_search_matches(self):
        search_matches = []
        for field in self.category.fields.all():
            if field.key in self.properties.keys():

                if field.fieldtype == 'LookupField':
                    l_id = self.properties.get(field.key)
                    if l_id is not None:
                        lookup = field.lookupvalues.get(pk=l_id)
                        search_matches.append('%s:%s' % (
                            field.key, lookup.name
                        ))

                elif field.fieldtype == 'MultipleLookupField':
                    values = self.properties.get(field.key)
                    if values is not None:
                        lookups = []

                        for l_id in values:
                            lookups.append(
                                field.lookupvalues.get(pk=l_id).name
                            )

                        search_matches.append('%s:%s' % (
                            field.key,
                            ', '.join(lookups))
                        )

                else:
                    term = self.properties.get(field.key)
                    if term is not None:
                        search_matches.append(
                            '%s:%s' % (field.key, term)
                        )

        self.search_matches = '#####'.join(search_matches)

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = OBSERVATION_STATUS.deleted
        self.save()


@receiver(pre_save, sender=Observation)
def pre_save_update(sender, **kwargs):
    observation = kwargs.get('instance')

    observation.update_display_field()
    observation.update_search_matches()


class Comment(models.Model):
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
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.responses.all().delete()
        self.status = COMMENT_STATUS.deleted
        self.save()


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
        """
        raise NotImplementedError(
            'The property `type_name` has not been implemented for this '
            'subclass of `MediaFile`.'
        )

    def delete(self):
        """
        Deletes a file by setting its status to active
        """
        self.status = MEDIA_STATUS.deleted
        self.save()


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
        Returns 'ImageFile'
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
        Returns 'VideoFile'
        """
        return 'VideoFile'
