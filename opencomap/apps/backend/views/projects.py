from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.choice import STATUS_TYPES

def projects_list(user):
	result = []
	projects = Project.objects.exclude(status=STATUS_TYPES['DELETED'])

	for project in projects:
		if (project.admins.isMember(user)) or ((not project.isprivate or project.contributors.isMember(user)) and project.status != STATUS_TYPES['INACTIVE']):
			result.append(project)
		
	return result

def project(user, project_id):
	project = Project.objects.get(pk=project_id)
	# TODO: Implement user check
	return project

def updateProject(user, project_id, data):
	project = Project.objects.get(pk=project_id)
	# TODO: Implement user check
	project.update(description=data.get('description'))
	return project