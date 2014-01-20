from opencomap.apps.backend.models.projects import Project

from django.core.exceptions import PermissionDenied
from decorators import check_admin

@check_admin
def update(user, project_id, featuretype_id, data, project=None):
	featuretype = project.featuretype_set.get(pk=featuretype_id)
	if data.get('description') != None: featuretype.update(description=data.get('description'))
	if data.get('status') != None: featuretype.update(status=data.get('status'))
	return featuretype

@check_admin
def delete(user, project_id, featuretype_id, project=None):
	featuretype = project.featuretype_set.get(pk=featuretype_id)
	featuretype.delete()
	return featuretype