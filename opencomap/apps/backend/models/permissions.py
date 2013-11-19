from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.layers import Layer

class UserGroup(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	can_admin = models.BooleanField(default=False)
	can_edit = models.BooleanField(default=False)
	can_contribute = models.BooleanField(default=False)
	can_view = models.BooleanField(default=True)
	users = models.ManyToManyField(settings.AUTH_USER_MODEL)
	project = models.ForeignKey(Project)
	layer = models.ForeignKey(Layer, null=True)
	is_admin = models.BooleanField(default=False)
	is_everyone = models.BooleanField(default=False)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + '. View: ' + str(self.can_view) + '. Edit: ' + str(self.can_edit) + '. Contribute: ' + str(self.can_contribute) + '. Admin: ' + str(self.can_admin)

	def addUsers(self, *users):
		for user in users:
			self.users.add(user)

	def removeUsers(self, *users):
		for user in users:
			self.users.remove(user)