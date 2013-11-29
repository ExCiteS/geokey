from django.db import models
from opencomap.apps.backend.models.permission import UserGroup

class Authenticatable(models.Model):
	"""
	Abstract class that provides functionality to link `Project` and `Layer` to `UserGroups`
	and provide checks for user permissions.
	"""
	usergroups = models.ManyToManyField(UserGroup)

	class Meta: 
		app_label = 'backend'
		abstract = True

	def _checkPermission(self, user, accessType):
		"""
		Checks if a user has permission to perform a task and returns if `True` or `False`.
		"""
		canDo = self.usergroups.filter(is_everyone=True).values()[0][accessType]

		if not canDo: 
			for group in self.usergroups.filter(users__id__exact=user.id).values():
				if group[accessType]: canDo = True

		return canDo


	def userCanRead(self, user):
		"""
		Checks if the user can read the data and returns if `True` or `False`.

		:user: The user to be checked.
		"""
		return self._checkPermission(user, 'can_read')


	def userCanView(self, user):
		"""
		Checks if the user can view graphical representations of the data and 
		returns if `True` or `False`.

		:user: The user to be checked.
		"""
		return self._checkPermission(user, 'can_view')


	def userCanContribute(self, user):
		"""
		Checks if the user can contribute data and returns if `True` or `False`.

		:user: The user to be checked.
		"""
		return self._checkPermission(user, 'can_contribute')


	def userCanEdit(self, user):
		"""
		Checks if the user can edit existing data and returns if `True` or `False`.

		:user: The user to be checked.
		"""
		return self._checkPermission(user, 'can_edit')


	def userCanAdmin(self, user):
		"""
		Checks if the user can administer the entity and returns if `True` or `False`.

		:user: The user to be checked.
		"""
		return self._checkPermission(user, 'can_admin')


	def getUserGroups(self):
		"""
		Returns all `UserGroups` assigned to the entity.
		"""
		return self.usergroups.all()


	def addUserGroups(self, *groups):
		"""
		Adds `UserGroups` to the entity.

		:groups: An arbitrary number of groups to be added to the entity.
		"""
		for group in groups:
			self.usergroups.add(group)


	def removeUserGroups(self, *groups):
		"""
		Removes `UserGroups` from the entity.

		:groups: An arbitrary number of groups to be removed from the entity.
		"""
		for group in groups:
			self.usergroups.remove(group)