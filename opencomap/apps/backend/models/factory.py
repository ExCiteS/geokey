from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.permissions import UserGroup

class Factory(object):
	class Meta: 
		app_label = 'backend'

	def __init__(self):
		a = 1

	def createProject(self, name, description, creator):
		project = Project(name=name, description=description, creator=creator)
		project.save()

		adminGroup = UserGroup(name='Administrators', can_admin=True, can_edit=True, can_contribute=True, can_view=True, is_admin=True, project=project)
		adminGroup.save()
		adminGroup.addUsers(creator)
		everyoneGroup = UserGroup(name='Everyone', is_everyone=True, project=project)
		everyoneGroup.save()

		project.addUserGroups(creator, adminGroup, everyoneGroup)

		return project
