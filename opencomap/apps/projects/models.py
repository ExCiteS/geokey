from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from opencomap.apps.permissions.models import UserGroup
from opencomap.apps.layers.models import Layer

# ###################################
# PROJECT
# ###################################


class ProjectFactory(object):
	def create(name, description, creator):
		project = Project(name=name, description=description, creator=creator)
		project.save()
		initialiseUserGroups(project, creator)

		return project
	

class Project(models.Model):
	"""
	Stores a single project.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	#status = models.IntegerField(choices=STATUS_CHOICES, default=1)
	usergroups = models.ManyToManyField(UserGroup)
	layers = models.ManyToManyField(Layer)

	def __unicode__(self):
		return self.name + ', ' + self.description

	def addUserGroups(self, *groups):
		for group in groups:
			self.usergroups.add(group)

	def _checkPermission(self, user, accessType):
		canDo = self.usergroups.filter(public_group=True).values()[0][accessType]

		if not canDo: 
			for group in self.usergroups.filter(users__id__exact=user.id).values():
				if group[accessType]: canDo = True

		return canDo

	def userCanView(self, user):
		return self._checkPermission(user, 'can_view')

	def userCanContribute(self, user):
		return self._checkPermission(user, 'can_contribute')

	def userCanEdit(self, user):
		return self._checkPermission(user, 'can_edit')

	def userCanAdmin(self, user):
		return self._checkPermission(user, 'can_admin')

	def update(self, user, name=None, description=None, status=None):
		if (self.userCanEdit(user) or self.userCanAdmin(user)):
			if name: self.name = name
			if description: self.description = description
			if status: self.status = status

			return self
		else:
			raise Forbidden('You are not allowed to edit project ' + self.name)

	def remove(self, user):
		if (self.userCanAdmin(user)):
			self.status = 4
			self.save()
			return True
		else:
			raise Forbidden('You are not allowed to administer project ' + self.name)
