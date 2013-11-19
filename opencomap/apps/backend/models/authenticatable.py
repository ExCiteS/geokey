from django.db import models

class Authenticatable(models.Model):
	class Meta: 
		app_label = 'backend'
		abstract = True

	def _checkPermission(self, user, accessType):
		canDo = self.usergroup_set.filter(is_everyone=True).values()[0][accessType]

		if not canDo: 
			for group in self.usergroup_set.filter(users__id__exact=user.id).values():
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

	def getUserGroups(self, user):
		if (self.userCanAdmin(user)):
			return self.usergroup_set.all()

	def addUserGroups(self, user, *groups):
		if (self.creator.id == user.id or self.userCanAdmin(user)):
			for group in groups:
				group.project = self
		else:
			raise PermissionDenied('You are not allowed to administer project ' + self.name)

	def removeUserGroups(self, user, *groups):
		if (self.userCanAdmin(user)):
			for group in groups:
				group.delete()
		else:
			raise PermissionDenied('You are not allowed to administer project ' + self.name)