from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from django.core.exceptions import PermissionDenied

import json

from opencomap.libs.serializers import ObjectSerializer as Serializer
from opencomap.libs.decorators import handle_http_errors, handle_malformed

from opencomap.apps.backend import authorization
from opencomap.apps.backend.models.projects import Project

@login_required
@require_http_methods(["PUT", "DELETE"])
@handle_http_errors
def updateProject(request, project_id):
	if request.method == "PUT":
		project = authorization.projects.updateProject(request.user, project_id, json.loads(request.body))
		return HttpResponse('{ "project": ' + Serializer().serialize([project]) + "}")

	elif request.method == "DELETE":
		project = authorization.projects.deleteProject(request.user, project_id)
		return HttpResponse("The project has been deleted.")

@login_required
@require_http_methods(["PUT"])
@handle_malformed
@handle_http_errors
def addUserToGroup(request, project_id, group_id):
	group = authorization.projects.addUserToGroup(request.user, project_id, group_id, json.loads(request.body))
	return HttpResponse('{ "usergroup": ' + Serializer().serialize([group]) + "}")

@login_required
@require_http_methods(["DELETE"])
@handle_http_errors
def removeUserFromGroup(request, project_id, group_id, user_id):
	authorization.projects.removeUserFromGroup(request.user, project_id, group_id, user_id)
	return HttpResponse("The user has been successfully removed from the group.")