from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.permissions import UserGroup
from opencomap.apps.backend.models.permissions import Authenticatable
from opencomap.apps.backend.models.choices import STATUS_TYPES

# ###################################
# PROJECT
# ###################################


def ProjectFactory(name, description, creator):
	project = Project(name=name, description=description, creator=creator)
	project.save()
	project.createUserGroups()

	return project
	

class Project(Authenticatable):
	"""
	Stores a single project.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(choices=STATUS_TYPES, default=1)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', ' + self.description

	def update(self, user, name=None, description=None, status=None):
		if (self.userCanEdit(user) or self.userCanAdmin(user)):
			if name: self.name = name
			if description: self.description = description
			if status: self.status = status

			return self
		else:
			raise PermissionDenied('You are not allowed to edit project ' + self.name)

	def remove(self, user):
		if (self.userCanAdmin(user)):
			self.status = 4
			self.save()
			return True
		else:
			raise PermissionDenied('You are not allowed to administer project ' + self.name)

	def addLayers(self, user, *layers):
		if (self.userCanAdmin(user)):
			for layer in layers:
				layer.projects.add(self)

	def removeLayer(self, user, *layer):
		if (self.userCanAdmin(user)):
			for layer in layers:
				layer.projects.remove(self)