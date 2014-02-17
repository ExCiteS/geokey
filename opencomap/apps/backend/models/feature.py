from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from djorm_hstore.fields import DictionaryField
from django.contrib.gis.db import models as gis

from opencomap.apps.backend.models.choice import STATUS_TYPES


class Commendable(models.Model):
    """
    Abstract class for all `Models` that can have `Comment`s
    """
    class Meta:
        app_label = 'backend'
        abstract = True

    def getComments(self):
        """
        Returns all comments which statis is not `DELETED`
        """
        raise NotImplementedError(
            'The method `getCommets` has not been implemented for this child'
            'class of `Commendable`.'
        )

    def addComment(self, comment):
        """
        Adds a comment to the `Commendable`
        """
        comment.commentto = self
        comment.save()

    def removeComments(self, *comments):
        """
        Removes an arbitrary number of `Comment`s from the `Commendable` by
        setting it's `status` to `DELETED`
        """
        for comment in comments:
            comment.delete()


class Feature(Commendable):
    """
    Represents a location to which an arbitrary number of observations can be
    attached.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    geometry = gis.GeometryField(geography=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
    projects = models.ManyToManyField('Project')
    featuretype = models.ForeignKey('FeatureType')

    _ACCEPTED_STATUS = (
        STATUS_TYPES['ACTIVE'],
        STATUS_TYPES['INACTIVE'],
        STATUS_TYPES['REVIEW']
    )

    class Meta:
        app_label = 'backend'

    def __unicode__(self):
        return self.name + ',  ' + self.geometry.wkt

    def update(self, name=None, description=None, geometry=None, status=None):
        """
        Updates a feature. Checks if the status is of ACTIVE, INACTIVE or
        REVIEW otherwise raises ValidationError.
        """
        if ((status is None) or (status in self._ACCEPTED_STATUS)):
            if (name):
                self.name = name
            if (description):
                self.description = description
            if (geometry):
                self.geometry = geometry
            if (status):
                self.status = status

            self.save()
        else:
            raise ValidationError(
                'The status provided is invalid. Accepted values are ACTIVE,'
                'INACTIVE or REVIEW.'
            )

    def delete(self):
        """
        Deletes a layer by setting its status to deleted.
        """
        self.status = STATUS_TYPES['DELETED']
        self.save()

    def addObservation(self, observation):
        """
        Adds an observation to the featre. Input data is validated against
        the field definitions of the `Feature`'s `FeatureType`
        """
        observation.feature = self

        if observation.dataIsValid():
            observation.save()
        else:
            raise ValidationError(
                'One or more input values of characteristics do match'
                'validation criteria of input fields.'
            )

    def getObservations(self):
        """
        Returns all `Observations` assigned to the `Feature`, excluding those
        having status `INACTIVE` or `DELETED`.
        """
        return self.observation_set.exclude(status=STATUS_TYPES['INACTIVE'])

    def removeObservations(self, *observations):
        """
        Removes an arbitrary number of `Observation`s from the `Feature` by
        setting its status to `DELETED`.
        """
        for observation in observations:
            observation.delete()

    def getComments(self):
        """
        Returns all comments which statis is not `DELETED`
        """
        return self.featurecomment_set.exclude(status=STATUS_TYPES['DELETED'])


class Observation(Commendable):
    """
    Stores a single observation.
    """
    id = models.AutoField(primary_key=True)
    data = DictionaryField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    feature = models.ForeignKey('Feature')
    status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

    _ACCEPTED_STATUS = (
        STATUS_TYPES['ACTIVE'],
        STATUS_TYPES['REVIEW']
    )

    class Meta:
        app_label = 'backend'

    def update(self, status=None):
        """
        Updates a feature. Checks if the status is of ACTIVE, INACTIVE or
        REVIEW otherwise raises ValidationError.
        """
        if ((status is None) or (status in self._ACCEPTED_STATUS)):
            if (status):
                self.status = status

            self.save()
        else:
            raise ValidationError(
                'The status provided is invalid. Accepted values are ACTIVE, '
                'INACTIVE or REVIEW.')

    def delete(self):
        """
        Deletes an observation by setting its status to `DELETED`.
        """
        self.status = STATUS_TYPES['DELETED']
        self.save()

    def getValue(self, fieldId):
        """
        Returns the value of a single field of the `Observation`
        """
        field = self.feature.featuretype.getField(fieldId)
        if str(fieldId) in self.data:
            return field.convertFromString(self.data[str(fieldId)])
        else:
            raise KeyError('No value set for field ' + str(fieldId))

    def setValue(self, fieldId, value):
        """
        Sets the value for the field.
        """
        field = self.feature.featuretype.getField(fieldId)

        if field.validateInput(value):
            self.data[str(fieldId)] = value
            self.save()
        else:
            raise ValidationError(
                'The input value does not match validation criteria of input'
                'fields.'
            )

    def deleteValue(self, fieldId):
        """
        Removes the value from the observation if the field is not required.
        """
        field = self.feature.featuretype.getField(fieldId)
        if not field.required:
            del self.data[str(fieldId)]
            self.save()
        else:
            raise ValidationError(
                'The value for field ' + str(fieldId) + ' cannot be deleted.'
                'The field is required.'
            )

    def dataIsValid(self, data=None):
        valid = True

        if not data:
            data = self.data

        for f in self.feature.featuretype.getFields():
            field = f.getInstance()

            if field.required and not (str(field.id) in data.keys()):
                valid = False

            if valid and not field.validateInput(data.get(str(field.id))):
                valid = False

        return valid

    def getComments(self):
        """
        Returns all comments which statis is not `DELETED`
        """
        return self.observationcomment_set
