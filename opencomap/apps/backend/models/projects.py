from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.authenticatable import Authenticatable
from opencomap.apps.backend.models.permissions import UserGroup
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
	usergroups = models.ManyToManyField(UserGroup)

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


	def getFeatures(self):
		"""
		Returns a list of all features assinged to the project. Excludes those having status `RETIRED` and `DELETED`
		"""

		resultSet = []
		for feature in self.feature_set.exclude(status=STATUS_TYPES['RETIRED']).exclude(status=STATUS_TYPES['DELETED']):
			resultSet.append(feature)

		return resultSet


	def addFeatures(self, *features):
		"""
		Adds an arbitrary number of features to the project.

		:features: The features to be added.
		"""

		for feature in features:
			feature.projects.add(self)


	def removeFeatures(self, *features):
		"""
		Removes an arbitrary number of features from the project.

		:features: The features to be removed.
		"""

		for feature in features:
			feature.projects.remove(self)