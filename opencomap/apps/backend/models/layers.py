from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.permissions import UserGroup
from opencomap.apps.backend.models.permissions import Authenticatable
from opencomap.apps.backend.models.projects import Project

TYPE_CHOICE = (
	(1, 'Text'),
	(2, 'Numeric'),
	(3, 'Lookup')
)

def LayerFactory(name, description, creator):
	layer = Layer(name=name, description=description, creator=creator)
	layer.save()
	layer.createUserGroups()
	
	return layer

class Layer(Authenticatable):
	"""
	Stores a single layer. Releated to :model:'api:Project'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	#status = models.IntegerField(choices=STATUS_CHOICES, default=1)
	projects = models.ManyToManyField(Project)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', '.join([p.name for p in self.project.all()])

	def update(self, user, name=None, description=None, status=None):
		if (self.userCanEdit(user) or self.userCanAdmin(user)):
			if name: self.name = name
			if description: self.description = description
			if status: self.status = status

			return self
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The layer has not been updated.')

	def remove(self, user):
		if (self.userCanAdmin(user)):
			self.status = 4
			self.save()
			return True
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The layer has not been deleted.')

	def addFields(self, user, *fields):
		if (self.userCanAdmin(user)):
			for field in fields:
				field.layer = self
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The field has not been added to the layer.')

	def removeFields(self, user, *fields):
		if (self.userCanAdmin(user)):
			for field in fields:
				field.delete()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The field has not been removed.')


class Field(models.Model):
	"""
	Stores a field. Releated to :model:'api:Layer'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField()
	required = models.BooleanField(default=False)
	minval = models.FloatField(null=True)
	maxval = models.FloatField(null=True)
	layer = models.ForeignKey(Layer)

	class Meta: 
		app_label = 'backend'

	def addLookupValues(self, user, *lookups):
		if (self.layer.userCanAdmin(user)):
			for value in lookups:
				value.field = self
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.layer.name + '. The lookup values have not been added.')

	def removeLookupValues(self, user, *lookups):
		if (self.layer.userCanAdmin(user)):
			for value in lookups:
				values.delete()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.layer.name + '. The lookup values have not been removed.')
			

class Lookup(models.Model):
	"""
	Stores a lookup value. Releated to :model:'api:Field'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	field = models.ForeignKey(Field)

	class Meta: 
		app_label = 'backend'