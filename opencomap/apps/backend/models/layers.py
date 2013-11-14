from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.permissions import UserGroup
from opencomap.apps.backend.models.permissions import Authenticatable
from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.choices import STATUS_TYPES

def LayerFactory(name, description, creator):
	layer = Layer(name=name, description=description, creator=creator)
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
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	projects = models.ManyToManyField(Project)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', '.join([p.name for p in self.project.all()])

	def update(self, user, name=None, description=None):
		if (self.userCanAdmin(user)):
			if name: self.name = name
			if description: self.description = description
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The layer has not been updated.')

	def setStatus(self, user, status):
		if (self.userCanAdmin(user)):
			self.status = status
			self.save()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The status has not been updated.')		

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
				field.save()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The field has not been added to the layer.')

	def removeFields(self, user, *fields):
		if (self.userCanAdmin(user)):
			for field in fields:
				field.delete()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The field has not been removed.')

	def getFeatures(self, user):
		resultSet = []
		for feature in self.feature_set.exclude(status=STATUS_TYPES['RETIRED']).exclude(status=STATUS_TYPES['DELETED']):
			if feature.userCanView(user): resultSet.append(feature)

		return resultSet


	def addFeatures(self, user, *features):
		if (self.userCanContribute(user)):
			for feature in features:
				feature.layer = self
				feature.save()
		else:
			raise PermissionDenied('You have no permission to contribute to layer ' + self.name + '. The feature has not been added to the layer.')

	def removeFeatures(self, user, *features):
		if (self.userCanEdit(user)):
			for feature in features:
				feature.status = 4
				feature.save()
		else:
			raise PermissionDenied('You have no permission to contribute to layer ' + self.name + '. The feature has not been removed from the layer.')