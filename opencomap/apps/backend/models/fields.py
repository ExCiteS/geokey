from django.db import models

from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.choices import STATUS_TYPES
from django.core.exceptions import PermissionDenied

class FeatureType(models.Model):
	"""
	Defines the data structure of a certain type of features. 
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField()
	project = models.ForeignKey(Project)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

	class Meta: 
		app_label = 'backend'

	def removeFields(self, *fields):
		"""
		Removes fields from the feature type

		:fields: The fields to be me removed.
		"""
		for field in fields:
			field.status = STATUS_TYPES['INACTIVE']
			field.save()

	def getFields(self):
		"""
		Returns all currently active fields af the feature type
		"""
		return self.field_set.exclude(status=STATUS_TYPES['INACTIVE'])


class Field(models.Model):
	"""
	A Field defines data type of one characterictic of an obesrvation. Used to create forms of
	user interfaces and to validate user inputs. 
	"""
	
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField()
	required = models.BooleanField(default=False)
	featuretype = models.ForeignKey(FeatureType)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

	class Meta: 
		app_label = 'backend'

class TextField(Field):
	class Meta: 
		app_label = 'backend'

	def validateInput(self, input):
		valid = True
		return valid

class NumericField(Field):
	minval = models.FloatField(null=True)
	maxval = models.FloatField(null=True)

	class Meta: 
		app_label = 'backend'

	def validateInput(self, input):
		valid = True
		return valid

class DateTimeField(Field):
	
	class Meta: 
		app_label = 'backend'

	def validateInput(self, input):
		valid = True
		return valid

class TrueFalseField(Field):
	
	class Meta: 
		app_label = 'backend'

	def validateInput(self, input):
		valid = True
		return valid

class LookupField(Field):
	"""
	A lookup value is a special kind of field the provides an pre-defined number of values 
	as valid input values.
	"""

	class Meta: 
		app_label = 'backend'

	def getLookupValues(self):
		"""
		Returns all currently active lookup values
		"""
		return self.lookupvalue_set.exclude(status=STATUS_TYPES['INACTIVE'])

	def addLookupValues(self, *lookups):
		"""
		Adds an arbitrary number of lookup values to the lookup field.

		:lookups: Lookup values to be added to the field.
		"""
		for value in lookups:
			LookupValue(name=value, field=self).save()

	def removeLookupValues(self, *lookups):
		"""
		Removes an arbitrary number of lookup values from the lookup field by setting
		its status to inactive.

		:lookups: Lookup values to be added to the field.
		"""
		for value in lookups:
			value.status = STATUS_TYPES['INACTIVE']
			value.save()

	def validateInput(self, input):
		valid = True
		return valid

class LookupValue(models.Model):
	"""
	Stores a single lookup value.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	field = models.ForeignKey(LookupField)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

	class Meta: 
		app_label = 'backend'