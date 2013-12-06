from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.feature import Feature
from opencomap.apps.backend.models.choice import STATUS_TYPES

class View(models.Model):

	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	created_at = models.DateTimeField(default=datetime.now(tz=utc))
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	projects = models.ManyToManyField(Project)
	features = models.ManyToManyField(Feature)

	class Meta: 
		app_label = 'backend'

	
	def getUserGroups(self):
		"""
		Returns all `ViewGroups` assigned to the `View`.
		"""
		return self.viewgroup_set.all()


	def addUserGroup(self, group):
		"""
		Adds a `ViewGroup` to the `View`.

		:group: The group to be added to the `View`.
		"""
		group.view = self
		group.save()


	def removeUserGroups(self, *groups):
		"""
		Removes `ViewGroups` from the `View` by deleting the `ViewGroup`.

		:groups: An arbitrary number of groups to be removed from the `View`.
		"""
		for group in groups:
			group.delete()

	# TODO: Implement permission checks. Mind the everyonegroup

	# def _checkPermission(self, user, accessType):
	# 	"""
	# 	Checks if a user has permission to perform a task and returns if `True` or `False`.
	# 	"""
	# 	canDo = self.usergroups.filter(is_everyone=True).values()[0][accessType]

	# 	if not canDo: 
	# 		for group in self.usergroups.filter(users__id__exact=user.id).values():
	# 			if group[accessType]: canDo = True

	# 	return canDo

	# def userCanRead(self, user):
	# 	"""
	# 	Checks if the user can read the data and returns if `True` or `False`.

	# 	:user: The user to be checked.
	# 	"""
	# 	return self._checkPermission(user, 'can_read')


	# def userCanView(self, user):
	# 	"""
	# 	Checks if the user can view graphical representations of the data and 
	# 	returns if `True` or `False`.

	# 	:user: The user to be checked.
	# 	"""
	# 	return self._checkPermission(user, 'can_view')

	# def userCanEdit(self, user):
	# 	"""
	# 	Checks if the user can edit existing data and returns if `True` or `False`.

	# 	:user: The user to be checked.
	# 	"""
	# 	return self._checkPermission(user, 'can_edit')


	# def userCanAdmin(self, user):
	# 	"""
	# 	Checks if the user can administer the entity and returns if `True` or `False`.

	# 	:user: The user to be checked.
	# 	"""
	# 	return self._checkPermission(user, 'can_admin')