from django.db import models

import iso8601

from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.libs.decorators import check_status
from opencomap.apps.backend.libs.managers import Manager

class FeatureType(models.Model):
	"""
	Defines the data structure of a certain type of features. 
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField()
	project = models.ForeignKey(Project)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

	objects = Manager()

	class Meta: 
		app_label = 'backend'

	@check_status
	def update(self, name=None, description=None, status=None):
		if (name): self.name = name
		if (description): self.description = description
		if (status != None): self.status = status

		self.save()

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

	def getField(self, fieldId):
		"""
		Returns exactly one `Field` identified by `id`
		"""
		return self.field_set.get(pk=fieldId).getInstance()



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

	objects = Manager()

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name

	def getInstance(self):
		"""
		Returns the child instance of the fields. When getting all fields from a feature type only the parent field
		instances are return; i.e. fields and methods of child instances are not given.
		"""
		try: 
			return self.textfield 
		except Field.DoesNotExist: 
			pass
		try: 
			return self.numericfield 
		except Field.DoesNotExist: 
			pass
		try: 
			return self.truefalsefield 
		except Field.DoesNotExist: 
			pass
		try: 
			return self.lookupfield 
		except Field.DoesNotExist: 
			pass
		try: 
			return self.datetimefield 
		except Field.DoesNotExist: 
			pass

	
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

	@check_status
	def update(self, name=None, description=None, status=None, required=None):
		if (name): self.name = name
		if (description): self.description = description
		if (status != None): self.status = status
		if (required != None): self.required = required

		self.save()


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

	def update(self, name=None, description=None, status=None, required=None, minval=None, maxval=None):
		self.minval = minval
		self.maxval = maxval

		self.save()
		
		super(NumericField, self).update(name=name, description=description, status=status, required=required)



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
		return value in [True, 'True', 'true', '1', 't', 1]



class DateTimeField(Field):
	"""
	A field for storing dates and times.
	"""
	class Meta: 
		app_label = 'backend'

	def validateInput(self, value):
		"""
		Checks if the provided value is a valid and ISO8601 compliant date string.
		"""
		
		try: 
			iso8601.parse_date(value)
			return True
		except iso8601.iso8601.ParseError: 
			return False
		



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

	objects = Manager()

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name

	@check_status
	def update(self, status=None):
		"""
		Updates the status pf the lookup.
		"""
		if status != None: self.status = status
		self.save()



FIELD_TYPES = {
	'TEXT': {
		'type_id': 0,
		'name': 'Text',
		'model': TextField
	},
	'NUMBER': {
		'type_id': 1,
		'name': 'Numeric',
		'model': NumericField
	},
	'TRUEFALSE': {
		'type_id': 2,
		'name': 'True/False',
		'model': TrueFalseField
	},
	'LOOKUP': {
		'type_id': 3,
		'name': 'Lookup',
		'model': LookupField
	},
	'DATETIME': {
		'type_id': 4,
		'name': 'Date and Time',
		'model': DateTimeField
	}
}