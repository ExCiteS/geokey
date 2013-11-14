from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.core.exceptions import PermissionDenied

class UserGroup(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	can_admin = models.BooleanField(default=False)
	can_edit = models.BooleanField(default=False)
	can_contribute = models.BooleanField(default=False)
	can_view = models.BooleanField(default=True)
	users = models.ManyToManyField(settings.AUTH_USER_MODEL)
	public_group = models.BooleanField(default=False)

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


class Authenticatable(models.Model):
	usergroups = models.ManyToManyField(UserGroup)

	class Meta: 
		app_label = 'backend'
		abstract = True

	def _checkPermission(self, user, accessType):
		canDo = self.usergroups.filter(public_group=True).values()[0][accessType]

		if not canDo: 
			for group in self.usergroups.filter(users__id__exact=user.id).values():
				if group[accessType]: canDo = True

		return canDo

	def createUserGroups(self):
		self.save()
		adminGroup = UserGroup(name='Admin', can_admin=True, can_edit=True, can_contribute=True, can_view=True)
		adminGroup.save()
		adminGroup.addUsers(self.creator)

		generalGroup = UserGroup(name='General public', public_group=True)
		generalGroup.save()

		self.usergroups.add(adminGroup, generalGroup)

	def userCanView(self, user):
		return self._checkPermission(user, 'can_view')

	def userCanContribute(self, user):
		return self._checkPermission(user, 'can_contribute')

	def userCanEdit(self, user):
		return self._checkPermission(user, 'can_edit')

	def userCanAdmin(self, user):
		return self._checkPermission(user, 'can_admin')

	def addUserGroups(self, user, *groups):
		if (self.creator.id == user.id or self.userCanAdmin(user)):
			for group in groups:
				self.usergroups.add(group)
		else:
			raise PermissionDenied('You are not allowed to administer project ' + self.name)

	def removeUserGroups(self, user, *groups):
		if (self.userCanAdmin(user)):
			for group in groups:
				self.usergroups.remove(group)
		else:
			raise PermissionDenied('You are not allowed to administer project ' + self.name)