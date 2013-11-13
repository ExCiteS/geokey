from django.db import models

from opencomap.apps.backend.models.layers import Layer
from django.core.exceptions import PermissionDenied

class Field(models.Model):
	"""
	Stores a field. Releated to :model:'api:Layer'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField()
	required = models.BooleanField(default=False)
	layer = models.ForeignKey(Layer)

	class Meta: 
		app_label = 'backend'

	def update(self, user, name=None, description=None, required=None, minval=None, maxval=None):
		if self.layer.userCanAdmin(user):
			if name: self.name = name
			if description: self.description = description
			if required: self.required = required
			if minval: self.minval = minval
			if maxval: self.maxval = maxval
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.layer.name + '. The field has not been updated.')

class TextField(Field):
	datatype = 1

	class Meta: 
		app_label = 'backend'

class NumericField(Field):
	datatype = 2
	minval = models.FloatField(null=True)
	maxval = models.FloatField(null=True)

	class Meta: 
		app_label = 'backend'

class DateTimeField(Field):
	datatype = 4

	class Meta: 
		app_label = 'backend'

class TrueFalseField(Field):
	datatype = 5

	class Meta: 
		app_label = 'backend'

class LookupField(Field):
	datatype = 3

	class Meta: 
		app_label = 'backend'

	def addLookupValues(self, user, *lookups):
		if (self.layer.userCanAdmin(user)):
			for value in lookups:
				LookupValue(name=value, field=self).save()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.layer.name + '. The lookup values have not been added.')

	def removeLookupValues(self, user, *lookups):
		if (self.layer.userCanAdmin(user)):
			for value in lookups:
				value.delete()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.layer.name + '. The lookup values have not been removed.')

class LookupValue(models.Model):
	"""
	Stores a lookup value. Releated to :model:'api:Field'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	field = models.ForeignKey(LookupField)

	class Meta: 
		app_label = 'backend'