from django.db import models
from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from djorm_hstore.fields import DictionaryField
from django.contrib.gis.db import models as gis
from django.core.exceptions import ValidationError

from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.fields import FeatureType
from opencomap.apps.backend.models.choices import STATUS_TYPES

class Feature(models.Model):
	"""
	Represents a location to which an arbitrary number of observations can be attached.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	geometry = gis.GeometryField(geography=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	projects = models.ManyToManyField(Project)
	featuretype = models.ForeignKey(FeatureType)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ',  ' + self.geometry.wkt

	def remove(self):
		"""
		Deletes a layer by setting its status to deleted.
		"""
		self.status = STATUS_TYPES['DELETED']
		self.save()

	def addObservation(self, observation):
		"""
		Adds an observation to the featre. Input data is validated against the field definitions of the `Feature`'s `FeatureType`
		"""
		valid = True

		for f in self.featuretype.getFields():
			field = self.featuretype.getField(f.name)

			if field.required and not (field.name in observation.data.keys()): 
				valid = False
				raise ValidationError('Required field ' + field.name + ' is not set or empty.')

		if valid and field.validateInput(observation.data.get(field.name)):
			observation.feature = self
			observation.save()
		else:
			raise ValidationError('One or more input values of characteristics do match validation criteria of input fields.')


	def getObservations(self):
		"""
		Returns all `Observations` assigned to the `Feature`, excluding those having status `INACTIVE` or `DELETED`.
		"""
		return self.observation_set.exclude(status=STATUS_TYPES['INACTIVE']).exclude(status=STATUS_TYPES['DELETED'])

	def removeObservations(self, *observations):
		"""
		Removes an `Observations` from the `Feature` by setting its status to `DELETED`.
		"""
		for observation in observations:
			observation.status = STATUS_TYPES['DELETED']
			observation.save()


class Observation(models.Model):
	"""
	Stores a single observation. 
	"""
	id = models.AutoField(primary_key=True)
	data = DictionaryField(db_index=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	feature = models.ForeignKey(Feature)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

	class Meta: 
		app_label = 'backend'

	def getValue(self, fieldName):
		"""
		Returns the value of a single field of the `Observation`
		"""
		field = self.feature.featuretype.getField(fieldName)
		return field.convertFromString(self.data[fieldName])