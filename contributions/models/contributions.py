import json
from pytz import utc
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save

from django_hstore import hstore
from simple_history.models import HistoricalRecords

from core.exceptions import InputError

from ..base import OBSERVATION_STATUS, COMMENT_STATUS
from ..manager import ObservationManager, CommentManager


class Observation(models.Model):
    """
    Stores a single observation.
    """
    location = models.ForeignKey(
        'contributions.Location', related_name='locations'
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
    review_comment = models.TextField(blank=True, null=True)
    attributes = hstore.DictionaryField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='creator'
    )
    updated_at = models.DateTimeField(null=True)
    updator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='updator',
        null=True
    )
    version = models.IntegerField(default=1)
    search_matches = models.TextField()

    history = HistoricalRecords()
    objects = ObservationManager()

    class Meta:
        ordering = ['updated_at', 'id']
        app_label = 'contributions'

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
    def replace_null(self, attributes):
        for key, value in attributes.iteritems():
            if isinstance(value, (str, unicode)) and len(value) == 0:
                attributes[key] = None

        return attributes

    @classmethod
    def create(cls, attributes=None, creator=None, location=None,
               category=None, project=None, status=None):
        """
        Creates a new observation. Validates all fields first and raises a
        ValidationError if at least one field did not validate.
        Creates the object if all fields are valid.
        """
        attributes = cls.replace_null(attributes)

        if status is None:
            status = category.default_status

        if status == 'draft':
            cls.validate_partial(category, attributes)
        else:
            cls.validate_full(category, attributes)

        location.save()
        observation = cls.objects.create(
            location=location,
            category=category,
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
            self.validate_partial(self.category, update)
        else:
            self.validate_full(self.category, update)
            self.version = self.version + 1

        if status == 'pending':
            self.review_comment = review_comment

        if status == 'active':
            self.review_comment = None

        self.attributes = update
        self.updator = updator
        self.status = status or self.status
        self.updated_at = datetime.utcnow().replace(tzinfo=utc)

        self.save()
        return self

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = OBSERVATION_STATUS.deleted
        self.save()


@receiver(pre_save, sender=Observation)
def update_search_matches(sender, **kwargs):
    observation = kwargs.get('instance')
    search_matches = []

    for field in observation.category.fields.all():
        if field.key in observation.attributes.keys():

            if field.fieldtype == 'TextField':
                term = observation.attributes.get(field.key)
                if term is not None:
                    search_matches.append('%s:%s' % (field.key, term))

            elif field.fieldtype == 'LookupField':
                l_id = observation.attributes.get(field.key)
                if l_id is not None:
                    lookup = field.lookupvalues.get(pk=l_id)
                    search_matches.append('%s:%s' % (field.key, lookup.name))

            elif field.fieldtype == 'MultipleLookupField':
                values = observation.attributes.get(field.key)
                if values is not None:
                    l_ids = json.loads(values)

                    for l_id in l_ids:
                        lookup = field.lookupvalues.get(pk=l_id)
                        search_matches.append('%s:%s' % (
                            field.key, lookup.name
                        ))

    observation.search_matches = '#####'.join(search_matches)


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

    class Meta:
        ordering = ['id']
        app_label = 'contributions'

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = COMMENT_STATUS.deleted
        self.save()
