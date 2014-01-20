from opencomap.apps.backend.models.projects import Project

from django.core.exceptions import PermissionDenied

def update(user, project_id, featuretype_id, data):
	project = Project.objects.get(pk=project_id)
	if project.admins.isMember(user):
		featuretype = project.featuretype_set.get(pk=featuretype_id)
		if data.get('description') != None: featuretype.update(description=data.get('description'))
		if data.get('status') != None: featuretype.update(status=data.get('status'))
		return featuretype
	else: 
		raise PermissionDenied('You are not allowed to update the settings of this project.')

def delete(user, project_id, featuretype_id):
	project = Project.objects.get(pk=project_id)
	if project.admins.isMember(user):
		featuretype = project.featuretype_set.get(pk=featuretype_id)
		featuretype.delete()
		return featuretype
	else: 
		raise PermissionDenied('You are not allowed to update the settings of this project.')