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
	Stores a single feature. Releated to :model:'api:Layer'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	geometry = gis.GeometryField(geography=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	project = models.ForeignKey(Project)
	featureType = models.ForeignKey(FeatureType)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', ' + self.layer.name + ', ' + self.geometry.wkt

	# def update(self, user, name=None, description=None):
	# 	if (self.userCanAdmin(user)):
	# 		if name: self.name = name
	# 		if description: self.description = description
	# 	else:
	# 		raise PermissionDenied('You have no permission to administer the feature ' + self.name + '. The feature has not been updated.')

	# def remove(self, user):
	# 	if (self.userCanAdmin(user)):
	# 		self.status = STATUS_TYPES['DELETED']
	# 		self.save()
	# 	else:
	# 		raise PermissionDenied('You have no permission to administer the feature ' + self.name + '. The feature has not been deleted.')

	# def setStatus(self, user, status):
	# 	if (self.userCanAdmin(user)):
	# 		self.status = status
	# 		self.save()
	# 	else:
	# 		raise PermissionDenied('You have no permission to administer the feature ' + self.name + '. The status has not been updated.')


class Observation(models.Model):
	"""
	Stores a single observation. Releated to :model:'api:Feature'
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