from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from djorm_hstore.fields import DictionaryField
from django.contrib.gis.db import models as gis

from opencomap.apps.backend.models.permissions import UserGroup
from opencomap.apps.backend.models.layers import Layer
from opencomap.apps.backend.models.choices import STATUS_TYPES

class Feature(models.Model):
	"""
	Stores a single feature. Releated to :model:'api:Layer'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	geometry = gis.GeometryField(geography=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(choices=STATUS_TYPES,default=1)
	usergroups = models.ManyToManyField(UserGroup)
	layer = models.ForeignKey(Layer)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', ' + self.layer.name + ', ' + self.geometry.wkt

	def addUserGroups(self, *groups):
		for group in groups:
			self.usergroups.add(group)

class Observation(models.Model):
	"""
	Stores a single observation. Releated to :model:'api:Feature'
	"""
	id = models.AutoField(primary_key=True)
	characteristics = DictionaryField(db_index=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	feature = models.ForeignKey(Feature)
	status = models.IntegerField(choices=STATUS_TYPES,default=1)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.feature.name # self.characteristics.items()