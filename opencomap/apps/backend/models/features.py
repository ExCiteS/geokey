from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from djorm_hstore.fields import DictionaryField
from django.contrib.gis.db import models as gis

from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.fields import FeatureType
from opencomap.apps.backend.models.choices import STATUS_TYPES

class Feature(models.Model):
	"""
	Represents a location to which an arbitrary number of observations can be attached.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	geometry = gis.GeometryField(geography=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	projects = models.ManyToManyField(Project)
	featuretype = models.ForeignKey(FeatureType)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', ' + self.layer.name + ', ' + self.geometry.wkt

	def remove(self):
		"""
		Deletes a layer by setting its status to deleted.
		"""
		self.status = STATUS_TYPES['DELETED']
		self.save()

	def getObservations(self):
		return self.observation_set.exclude(status=STATUS_TYPES['INACTIVE']).exclude(STATUS_TYPES['DELETED'])

	def removeObservations(self, *observations):
		for observation in observations:
			observation.status = STATUS_TYPES['DELETED']
			observation.save()


class Observation(models.Model):
	"""
	Stores a single observation. 
	"""
	id = models.AutoField(primary_key=True)
	characteristics = DictionaryField(db_index=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	feature = models.ForeignKey(Feature)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.feature.name # self.characteristics.items()

	# def save(self, *args, **kwargs):
	# 	"""
	# 	Overrides the `Model`'s `save` method in order to provide validation functionality
	# 	"""

		

	# 	super(Observation, self).save(*args, **kwargs)