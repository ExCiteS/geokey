from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.permissions import UserGroup

class Factory(object):
	"""
	Provides functionality to automate creation of projects and their default user groups.
	"""
	class Meta: 
		app_label = 'backend'

	def __init__(self):
		a = 1

	def createProject(self, name, description, creator):
		"""
		Creates a new project, adds to user groups to the projects and adds the creator to the group
		of project administrators. Returns the created project.

		:name: The name of the project.
		:description: The description of the project.
		:creator: The user who creates the project.
		"""
		project = Project(name=name, description=description, creator=creator)
		project.save()

		adminGroup = UserGroup(name='Administrators', can_admin=True, can_edit=True, can_contribute=True, can_read=True, can_view=True, is_admin=True)
		adminGroup.save()
		adminGroup.addUsers(creator)
		everyoneGroup = UserGroup(name='Everyone', is_everyone=True)
		everyoneGroup.save()

		project.addUserGroups(adminGroup, everyoneGroup)
		project.save()
		
		return project
