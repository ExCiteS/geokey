from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

def initialiseUserGroups(relation, creator):
	adminGroup = UserGroup(name='Admin', can_admin=True, can_edit=True, can_contribute=True, can_view=True)
	adminGroup.save()
	adminGroup.addUsers(creator)

	generalGroup = UserGroup(name='General public', public_group=True)
	generalGroup.save()

	relation.addUserGroups(adminGroup, generalGroup)

class UserGroup(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	can_admin = models.BooleanField(default=False)
	can_edit = models.BooleanField(default=False)
	can_contribute = models.BooleanField(default=False)
	can_view = models.BooleanField(default=True)
	users = models.ManyToManyField(settings.AUTH_USER_MODEL)
	public_group = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name + '. View: ' + str(self.can_view) + '. Edit: ' + str(self.can_edit) + '. Contribute: ' + str(self.can_contribute) + '. Admin: ' + str(self.can_admin)

	def addUsers(self, *users):
		for user in users:
			self.users.add(user)