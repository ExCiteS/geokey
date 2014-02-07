from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.usergroup import UserGroup

from opencomap.apps.backend.models.choice import STATUS_TYPES

from django.contrib.auth.models import User

from django.core.exceptions import PermissionDenied
from opencomap.libs.exceptions import MalformedBody
from decorators import check_admin

def get_list(user):
	"""
	Return a list of all projects, that are accessible to the user. The list may 
	be empty if the user is not eligible to access any projects.
	"""
	result = []
	projects = Project.objects.all()

	for project in projects:
		if project.isViewable(user):
			result.append(project)
		
	return result

def get_single(user, project_id):
	"""
	Returns a single project, or raises `PermissionDenied` if the user is 
	eligible to access the project.
	"""
	project = Project.objects.get(pk=project_id)
	if project.isViewable(user):
		return project
	else:
		raise PermissionDenied('You are not allowed to access this project.')

@check_admin
def update(user, project_id, data, project=None):
	"""
	Updates a project, or raises `PermissionDenied` if the user is 
	eligible to alter the project. Returns the project.
	"""
	if data.get('isprivate') != None: project.update(isprivate=data.get('isprivate'))
	if data.get('status') != None: project.update(status=data.get('status'))
	if data.get('description') != None: project.update(description=data.get('description'))
	if data.get('everyonecontributes') != None: project.update(everyonecontributes=data.get('everyonecontributes'))

	return project

@check_admin
def delete(user, project_id, project=None):
	"""
	Deletes a project, or raises `PermissionDenied` if the user is eligible 
	to alter the project.
	"""
	project.delete()
	return project

@check_admin
def add_user_to_group(user, project_id, group_id, userToAdd, project=None):
	"""
	Adds an existing user to either the contributors or administrators group, 
	or raises `PermissionDenied` if the user is eligible to alter the project.
	"""
	if project.admins.id == int(group_id) or project.contributors.id == int(group_id):
		group = UserGroup.objects.get(pk=group_id)
		try:
			user = User.objects.get(pk=userToAdd.get('userId'))
		except User.DoesNotExist, err:
			raise MalformedBody(err)
		group.addUsers(user)

		return group
	else:
		raise UserGroup.DoesNotExist

@check_admin
def remove_user_from_group(user, project_id, group_id, userToRemove, project=None):
	"""
	Adds an existing user to either the contributors or administrators group, 
	or raises `PermissionDenied` if the user is eligible to alter the project.
	"""
	if project.admins.id == int(group_id) or project.contributors.id == int(group_id):
		group = UserGroup.objects.get(pk=group_id)
		user = group.users.get(pk=userToRemove)

		group.removeUsers(user)
		return group
	else:
		raise UserGroup.DoesNotExist