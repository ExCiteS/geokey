from django.db import models

from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.models.choice import FIELD_TYPE

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

	def addField(self, field):
		field.featuretype = self
		field.save()

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

	def getField(self, name):
		"""
		Returns exactly one `Field` identified by name
		"""
		field = self.field_set.filter(name=name)[0]

		try: 
			return field.textfield 
		except Field.DoesNotExist: 
			pass
		try: 
			return field.numericfield 
		except Field.DoesNotExist: 
			pass
		try: 
			return field.truefalsefield 
		except Field.DoesNotExist: 
			pass
		try: 
			return field.lookupfield 
		except Field.DoesNotExist: 
			pass



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

	def __unicode__(self):
		return self.name

	
	def validateInput(self, value):
		"""
		Validates the given `value` against the field definition.
		@abstractmethod
		"""
		raise NotImplementedError('The method `validateInput` has not been implemented for this child class of Field.')


	def convertFromString(self, value):
		"""
		Converts the given `value` of an `Observation`'s field from `String` to the proper data type. By default returns simply 
		the value in `String` format. Needs to be overridden in order to support other data types.
		"""
		return value




class TextField(Field):
	"""
	A field for character strings.
	"""
	class Meta: 
		app_label = 'backend'

	def validateInput(self, value):
		"""
		Validates if the given value is a valid input for the `TextField` by checking if the provided value is of type `String`.
		Returns `True` or `False`.
		"""
		return isinstance(value, basestring)




class NumericField(Field):
	"""
	A field for numeric values.
	"""
	minval = models.FloatField(null=True)
	maxval = models.FloatField(null=True)

	class Meta: 
		app_label = 'backend'

	def validateInput(self, value):
		"""
		Validates if the given value is a valid input for the NumerField. Checks if a value of type number has been provided or if
		a value of type String has been provided that can be successfully converted to a Float value. Then checks if the value is 
		between bounds of minval and maxval. Returns `True` or `False`.
		"""
		valid = False

		if not isinstance(value, bool):
			try:
				value = float(value)
			except ValueError:
				pass
			
		valid = isinstance(value, float)

		if valid:
			if self.minval and self.maxval:
				valid = (value >= self.minval) and (value <= self.maxval)
			else: 
				if self.minval: valid = (value >= self.minval)
				if self.maxval: valid = (value <= self.maxval)

		return valid

	def convertFromString(self, value):
		"""
		Returns the `value` of the field in `Float` format.
		"""
		return float(value)



class TrueFalseField(Field):
	"""
	A field that can only have two states True and False.
	"""
	class Meta: 
		app_label = 'backend'

	def validateInput(self, value):
		"""
		Checks if the provided value is one of `True`, `False`, `'True'`, `'true'`, `'1'`, `'t'`, `'False'`, `'false'`, `'0'`, `'f'`, `0`, `1`.
		Returns `True` or `False`.
		"""
		return value in [True, False, 'True', 'true', '1', 't', 'False', 'false', '0', 'f', 0, 1]

	def convertFromString(self, value):
		"""
		Returns the `value` of the field in `Bool` format.
		"""
		return value in [True, 
		'True', 'true', '1', 't', 1]



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

	def validateInput(self, value):
		"""
		Checks if the provided value is in the list of `LookupValue`'s.	Returns `True` or `False`.
		"""
		valid = False
		for lookupvalue in self.lookupvalue_set.exclude(status=STATUS_TYPES['INACTIVE']).exclude(status=STATUS_TYPES['DELETED']):
			if lookupvalue.id == value: valid = True

		return valid

	def convertFromString(self, value):
		"""
		Returns the `value` of the field in `int` format.
		"""
		return int(value)


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

	def __unicode__(self):
		return self.name