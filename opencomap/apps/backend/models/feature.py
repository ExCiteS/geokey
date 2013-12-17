from django.db import models
from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from djorm_hstore.fields import DictionaryField
from django.contrib.gis.db import models as gis
from django.core.exceptions import ValidationError

from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.featuretype import FeatureType
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
		raise NotImplementedError('The method `getCommets` has not been implemented for this child class of `Commendable`.')

	def addComment(self, comment):
		"""
		Adds a comment to the `Commendable`
		"""
		comment.commentto = self
		comment.save()

	def removeComments(self, *comments):
		"""
		Removes an arbitrary number of `Comment`s from the `Commendable` by setting it's `status` to `DELETED`
		"""
		for comment in comments:
			comment.delete()

class Feature(Commendable):
	"""
	Represents a location to which an arbitrary number of observations can be attached.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	geometry = gis.GeometryField(geography=True)
	created_at = models.DateTimeField(auto_now_add=True)
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	projects = models.ManyToManyField(Project)
	featuretype = models.ForeignKey(FeatureType)

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
		Updates a feature. Checks if the status is of ACTIVE, INACTIVE or REVIEW otherwise raises ValidationError.
		"""
		if ((status is None) or (status in self._ACCEPTED_STATUS)):
			if (name): self.name = name
			if (description): self.description = description
			if (geometry): self.geometry = geometry
			if (status): self.status = status

			self.save()
		else:
			raise ValidationError('The status provided is invalid. Accepted values are ACTIVE, INACTIVE or REVIEW.')


	def delete(self):
		"""
		Deletes a layer by setting its status to deleted.
		"""
		self.status = STATUS_TYPES['DELETED']
		self.save()

	def addObservation(self, observation):
		"""
		Adds an observation to the featre. Input data is validated against the field definitions of the `Feature`'s `FeatureType`
		"""
		observation.feature = self

		if observation.dataIsValid():			
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
		Removes an arbitrary number of `Observation`s from the `Feature` by setting its status to `DELETED`.
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
	feature = models.ForeignKey(Feature)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

	_ACCEPTED_STATUS = (
		STATUS_TYPES['ACTIVE'], 
		STATUS_TYPES['REVIEW']
	)

	class Meta: 
		app_label = 'backend'

	def update(self, status=None):
		"""
		Updates a feature. Checks if the status is of ACTIVE, INACTIVE or REVIEW otherwise raises ValidationError.
		"""
		if ((status is None) or (status in self._ACCEPTED_STATUS)):
			if (status): self.status = status

			self.save()
		else:
			raise ValidationError('The status provided is invalid. Accepted values are ACTIVE, INACTIVE or REVIEW.')

	def delete(self):
		"""
		Deletes an observation by setting its status to `DELETED`.
		"""
		self.status = STATUS_TYPES['DELETED']
		self.save()

	def getValue(self, fieldName):
		"""
		Returns the value of a single field of the `Observation`
		"""
		field = self.feature.featuretype.getField(fieldName)
		if self.data.has_key(fieldName):
			return field.convertFromString(self.data[fieldName])
		else:
			raise KeyError('No value set for field ' + fieldName)

	def setValue(self, fieldName, value):
		"""
		Sets the value for the field.
		"""
		field = self.feature.featuretype.getField(fieldName)

		if field.validateInput(value):
			self.data[fieldName] = value
			self.save()
		else:
			raise ValidationError('The input value does not match validation criteria of input fields.')

	def deleteValue(self, fieldName):
		"""
		Removes the value from the observation if the field is not required.
		"""
		field = self.feature.featuretype.getField(fieldName)
		if not field.required:
			del self.data[fieldName]
			self.save()
		else:
			raise ValidationError('The value for field ' + fieldName + ' cannot be deleted. The field is required.')

	def dataIsValid(self, data=None):
		valid = True

		if not data: data = self.data
		
		for f in self.feature.featuretype.getFields():
			field = self.feature.featuretype.getField(f.name)

			if field.required and not (field.name in data.keys()): 
				valid = False
				
			if valid and not field.validateInput(data.get(field.name)):
				valid = False

		return valid

	def getComments(self):
		"""
		Returns all comments which statis is not `DELETED`
		"""
		return self.observationcomment_set.exclude(status=STATUS_TYPES['DELETED'])