from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from opencomap.apps.backend.models.permissions import UserGroup

TYPE_CHOICE = (
	(1, 'Text'),
	(2, 'Numeric'),
	(3, 'Lookup')
)

def createLayer(name, description, creator):
	layer = Layer(name=name, description=description, creator=creator)
	layer.save()
	initialiseUserGroups(layer, creator)

	return layer

class Layer(models.Model):
	"""
	Stores a single layer. Releated to :model:'api:Project'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	#status = models.IntegerField(choices=STATUS_CHOICES, default=1)
	usergroups = models.ManyToManyField(UserGroup)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', '.join([p.name for p in self.project.all()])

	def addUserGroups(self, *groups):
		for group in groups:
			self.usergroups.add(group)

	def addProjects(self, *projects):
		for project in projects:
			self.project.add(project)


class Field(models.Model):
	"""
	Stores a field. Releated to :model:'api:Layer'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField()
	required = models.BooleanField(default=False)
	minval = models.FloatField(null=True)
	maxval = models.FloatField(null=True)
	layer = models.ForeignKey(Layer)

	class Meta: 
		app_label = 'backend'

class Lookup(models.Model):
	"""
	Stores a lookup value. Releated to :model:'api:Field'
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	field = models.ForeignKey(Field)

	class Meta: 
		app_label = 'backend'