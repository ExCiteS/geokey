from django.db import models
from opencomap.apps.backend.models.view import View
from opencomap.apps.backend.models.usergroup import UserGroup

class ViewGroup(UserGroup):
	can_admin = models.BooleanField(default=False)
	can_edit = models.BooleanField(default=False)
	can_read = models.BooleanField(default=False)
	can_view = models.BooleanField(default=True)
	view = models.ForeignKey(View)

	class Meta: 
		app_label = 'backend'