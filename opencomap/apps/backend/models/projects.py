from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.authenticatable import Authenticatable
from opencomap.apps.backend.models.choices import STATUS_TYPES

class Project(Authenticatable):
	"""
	Stores a single project. Extends `Authenticatable`.
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

	def update(self, name=None, description=None, status=None):
		"""
		Updates `name` and `description of a project.

		:name: The new name of the project.
		:description: The new description of the project.
		:status: The new status of the project.
		"""

		if name: self.name = name
		if description: self.description = description
		if status: self.status = status
		self.save()


	def remove(self):
		"""
		Removes the project from the listing of all projects by setting its status to `DELETED`.
		"""

		self.status = STATUS_TYPES['DELETED']
		self.save()


	def getLayers(self):
		"""
		Returns a list of all layers assinged to the project. Excludes those having status `RETIRED` and `DELETED`
		"""

		resultSet = []
		for layer in self.layer_set.exclude(status=STATUS_TYPES['RETIRED']).exclude(status=STATUS_TYPES['DELETED']):
			resultSet.append(layer)

		return resultSet


	def addLayers(self, *layers):
		"""
		Adds an arbitrary number of layers to the project.

		:layers: The layers to be added.
		"""

		for layer in layers:
			layer.projects.add(self)


	def removeLayers(self, *layers):
		"""
		Removes an arbitrary number of layers from the project.

		:layers: The layers to be removed.
		"""

		for layer in layers:
			layer.projects.remove(self)