from django.db import models
from opencomap.apps.backend.models.view import View
from opencomap.apps.backend.models.usergroup import UserGroup
# from opencomap.apps.backend.libs.managers import Manager

class ViewGroup(UserGroup):
	can_edit = models.BooleanField(default=False)
	can_read = models.BooleanField(default=False)
	can_view = models.BooleanField(default=True)
	view = models.ForeignKey(View)

	# objects = Manager()

	class Meta: 
		app_label = 'backend'

	def update(self, description=None, can_edit=None, can_read=None, can_view=None):
		if description: self.description = description
		if can_edit != None: self.can_edit = can_edit
		if can_read != None: self.can_read = can_read
		if can_view != None: self.can_view = can_view

		self.save()

		return self