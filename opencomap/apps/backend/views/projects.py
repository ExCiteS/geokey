from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.choice import STATUS_TYPES

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied

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
		raise ObjectDoesNotExist('The requested project has been deleted by a project administrator.')
	else:
		raise ObjectDoesNotExist('You are not allowed to access this project.')

def deleteProject(user, project_id):
	project = Project.objects.get(pk=project_id)
	if project.admins.isMember(user):
		project.delete()
		return project
	else:
		raise PermissionDenied('You are not allowed to delete this project.') 

def updateProject(user, project_id, data):
	project = Project.objects.get(pk=project_id)
	if project.admins.isMember(user):
		project.update(description=data.get('description'))
		return project
	else: 
		raise PermissionDenied('You are not allowed to update the settings of this project.')