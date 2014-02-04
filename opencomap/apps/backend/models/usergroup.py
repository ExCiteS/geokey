from django.db import models
from django.conf import settings

class UserGroup(models.Model):
	"""
	Defines user permissions to layers and projects.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	users = models.ManyToManyField(settings.AUTH_USER_MODEL)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name

	def update(self, description=None, can_admin=None, can_edit=None, can_read=None, can_view=None):
		if description: self.description = description
		if can_admin != None: self.can_admin = can_admin
		if can_edit != None: self.can_edit = can_edit
		if can_read != None: self.can_read = can_read
		if can_view != None: self.can_view = can_view

		self.save()

		return self


	def addUsers(self, *users):
		"""
		Adds users to the group.

		:users: An arbitrary number of users to be added to the group.
		"""
		for user in users:
			self.users.add(user)

	def removeUsers(self, *users):
		"""
		Removes users from the group.

		:users: An arbitrary number of users to be remove fromgith the group.
		"""
		for user in users:
			self.users.remove(user)

	def isMember(self, user):
		"""
		Return `True` if the user is member of the group, `False` if not.
		"""
		return user in self.users.all()