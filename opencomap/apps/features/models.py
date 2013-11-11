from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from djorm_hstore.fields import DictionaryField
from django.contrib.gis.db import models as gis

from opencomap.apps.permissions.models import UserGroup
from opencomap.apps.layers.models import Layer

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
	#status = models.IntegerField(choices=STATUS_CHOICES,default=1)
	usergroups = models.ManyToManyField(UserGroup)
	layer = models.ForeignKey(Layer)

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
	#status = models.IntegerField(choices=STATUS_CHOICES,default=1)

	def __unicode__(self):
		return self.feature.name # self.characteristics.items()