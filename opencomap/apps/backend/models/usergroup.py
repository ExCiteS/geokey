from django.db import models
from django.conf import settings

class UserGroup(models.Model):
	"""
	Defines user permissions to layers and projects.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	users = models.ManyToManyField(settings.AUTH_USER_MODEL)

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name

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