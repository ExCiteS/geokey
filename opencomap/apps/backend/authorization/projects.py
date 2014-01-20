from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.usergroup import UserGroup

from opencomap.apps.backend.models.choice import STATUS_TYPES

from django.contrib.auth.models import User

from django.core.exceptions import PermissionDenied
from opencomap.libs.exceptions import MalformedBody
from decorators import check_admin

def projects_list(user):
	result = []
	projects = Project.objects.exclude(status=STATUS_TYPES['DELETED'])

	for project in projects:
		if (project.admins.isMember(user)) or ((not project.isprivate or project.contributors.isMember(user)) and project.status != STATUS_TYPES['INACTIVE']):
			result.append(project)
		
	return result

def project(user, project_id):
	project = Project.objects.get(pk=project_id)
	if ((project.admins.isMember(user)) or ((not project.isprivate or project.contributors.isMember(user)) and project.status != STATUS_TYPES['INACTIVE'])) and project.status != STATUS_TYPES['DELETED']:
		return project
	elif project.status == STATUS_TYPES['DELETED']:
		raise Project.DoesNotExist('The requested project has been deleted by a project administrator.')
	else:
		raise PermissionDenied('You are not allowed to access this project.')

def deleteProject(user, project_id):
	project = Project.objects.get(pk=project_id)
	if project.admins.isMember(user):
		project.delete()
		print project.status
		return project
	else: 
		raise PermissionDenied('You are not allowed to update the settings of this project.')

def updateProject(user, project_id, data):
	project = Project.objects.get(pk=project_id)
	if project.admins.isMember(user):
		if data.get('isprivate') != None: project.update(isprivate=data.get('isprivate'))
		if data.get('status') != None: project.update(status=data.get('status'))
		if data.get('description') != None: project.update(description=data.get('description'))

		return project
	else: 
		raise PermissionDenied('You are not allowed to update the settings of this project.')

def addUserToGroup(user, project_id, group_id, userToAdd):
	project = Project.objects.get(pk=project_id)
	if project.admins.isMember(user):
		if project.admins.id == int(group_id) or project.contributors.id == int(group_id):
			try:
				user = User.objects.get(pk=userToAdd.get('userId'))
			except User.DoesNotExist, err:
				raise MalformedBody(err)
			group = UserGroup.objects.get(pk=group_id)
			group.addUsers(user)

			return group
		else:
			raise UserGroup.DoesNotExist
	else: 
		raise PermissionDenied('You are not allowed to update the settings of this project.')

def removeUserFromGroup(user, project_id, group_id, userToRemove):
	project = Project.objects.get(pk=project_id)
	if project.admins.isMember(user):
		if project.admins.id == int(group_id) or project.contributors.id == int(group_id):
			group = UserGroup.objects.get(pk=group_id)
			user = User.objects.get(pk=userToRemove)
			if group.isMember(user):
				group.removeUsers(user)
				return group
			else:
				raise User.DoesNotExist	
		else:
			raise UserGroup.DoesNotExist
	else: 
		raise PermissionDenied('You are not allowed to update the settings of this project.')