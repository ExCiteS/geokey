from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.authenticatable import Authenticatable
from opencomap.apps.backend.models.choices import STATUS_TYPES

# ###################################
# PROJECT
# ###################################
	

class Project(Authenticatable):
	"""
	Stores a single project.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', ' + self.description

	def update(self, user, name=None, description=None, status=None):
		if (self.userCanEdit(user) or self.userCanAdmin(user)):
			if name: self.name = name
			if description: self.description = description
			self.save()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The project has not been updated.')

	def setStatus(self, user, status):
		if (self.userCanAdmin(user)):
			self.status = status
			self.save()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The status has not been set.')

	def remove(self, user):
		if (self.userCanAdmin(user)):
			self.status = 4
			self.save()
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The project has not been deleted.')

	def getLayers(self, user):
		resultSet = []
		for layer in self.layer_set.exclude(status=STATUS_TYPES['RETIRED']).exclude(status=STATUS_TYPES['DELETED']):
			if layer.userCanView(user): resultSet.append(layer)

		return resultSet

	def addLayers(self, user, *layers):
		if (self.userCanAdmin(user)):
			for layer in layers:
				layer.projects.add(self)
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The layers have not been added.')

	def removeLayers(self, user, *layers):
		if (self.userCanAdmin(user)):
			for layer in layers:
				layer.projects.remove(self)
		else:
			raise PermissionDenied('You have no permission to administer the layer ' + self.name + '. The layers has not been removed.')

