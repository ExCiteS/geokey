from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.core.exceptions import ValidationError

from opencomap.apps.backend.models.authenticatable import Authenticatable
from opencomap.apps.backend.models.choice import STATUS_TYPES

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

	_ACCEPTED_STATUS = (
		STATUS_TYPES['ACTIVE'], 
		STATUS_TYPES['INACTIVE']
	)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', ' + self.description

	def update(self, name=None, description=None, status=None):
		"""
		Updates a project. Checks if the status is of ACTIVE or INACTIVE otherwise raises ValidationError.
		"""
		if ((status is None) or (status in self._ACCEPTED_STATUS)):
			if (name): self.name = name
			if (description): self.description = description
			if (status): self.status = status

			self.save()
		else:
			raise ValidationError('The status provided is invalid. Accepted values are ACTIVE or INACTIVE')

	def delete(self):
		"""
		Removes the project from the listing of all projects by setting its status to `DELETED`.
		"""
		self.status = STATUS_TYPES['DELETED']
		self.save()

	def getFeatures(self):
		"""
		Returns a list of all features assinged to the project. Excludes those having status `RETIRED` and `DELETED`
		"""
		return self.feature_set.exclude(status=STATUS_TYPES['INACTIVE']).exclude(status=STATUS_TYPES['DELETED'])

	def addFeature(self, feature):
		"""
		Adds a feature to the project.

		:feature: The features to be added.
		"""
		feature.save()
		feature.projects.add(self)
		
	def removeFeatures(self, *features):
		"""
		Removes an arbitrary number of `Features`s from the `Project`.

		:feature: The feature to be removed.
		"""
		for feature in features:
			feature.projects.remove(self)
			feature.save()

	def getFeatureTypes(self):
		"""
		Returns all `FeatureTypes` assigned to the project
		"""
		return self.featuretype_set.exclude(status=STATUS_TYPES['INACTIVE']).exclude(status=STATUS_TYPES['DELETED'])

	def addFeatureType(self, featuretype):
		"""
		Adds a `FeatureType` to the project
		"""
		featuretype.project = self
		featuretype.save()


	def addView(self, view):
		"""
		Adds a `View` to the `Project`
		"""
		view.save()
		view.projects.add(self)

	def removeViews(self, *views):
		"""
		Removes an arbitraty number of `View`s from the `Project`
		"""
		for view in views:
			view.projects.remove(view)