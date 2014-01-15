from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from django.core.exceptions import PermissionDenied

import json

from opencomap.libs.serializers import SingleSerializer, ObjectSerializer
from opencomap.libs.decorators import handle_http_errors, handle_malformed

from opencomap.apps.backend.auth import projects as projectAuth
from opencomap.apps.backend.models.projects import Project

@login_required
@require_http_methods(["PUT", "DELETE"])
def updateProject(request, project_id):
	if request.method == "PUT":
		try: 
			project = projectAuth.updateProject(request.user, project_id, json.loads(request.body))
			serializer = SingleSerializer()
			return HttpResponse('{ "project": ' + serializer.serialize(project) + "}")
		except PermissionDenied, err:
			return HttpResponse(err, status=401)
		except Project.DoesNotExist, err:
			return HttpResponse(err, status=404)

	elif request.method == "DELETE":
		try: 
			project = projectAuth.deleteProject(request.user, project_id)
			return HttpResponse("The project has been deleted.")
		except PermissionDenied, err:
			return HttpResponse(err, status=401)
		except Project.DoesNotExist, err:
			return HttpResponse(err, status=404)

@login_required
@require_http_methods(["PUT"])
@handle_malformed
@handle_http_errors
def addUserToGroup(request, project_id, group_id):
	group = projectAuth.addUserToGroup(request.user, project_id, group_id, json.loads(request.body))
	serializer = SingleSerializer()
	return HttpResponse('{ "usergroup": ' + serializer.serialize(group) + "}")

@login_required
@require_http_methods(["DELETE"])
@handle_http_errors
def removeUserFromGroup(request, project_id, group_id, user_id):
	projectAuth.removeUserFromGroup(request.user, project_id, group_id, user_id)
	return HttpResponse("The user has been successfully removed from the group.")