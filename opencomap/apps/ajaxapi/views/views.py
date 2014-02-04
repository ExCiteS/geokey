import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from opencomap.libs.serializers import ObjectSerializer as Serializer
from opencomap.libs.decorators.http import handle_http_errors, handle_malformed
from opencomap.libs.views import render_to_json, render_to_success

from opencomap.apps.backend import authorization


@login_required
@require_http_methods(["PUT", "DELETE"])
@handle_http_errors
def update(request, project_id, view_id):
	if request.method == "PUT":
		view = authorization.views.update(request.user, project_id, view_id, json.loads(request.body))
		return render_to_json("view", Serializer().serialize(view))

	elif request.method == "DELETE":
		view = authorization.views.delete(request.user, project_id, view_id)
		return render_to_success("The view has been deleted.")

@login_required
@require_http_methods(["PUT"])
@handle_http_errors
@handle_malformed
def updateGroup(request, project_id, view_id, group_id):
	group = authorization.views.update_usergrpup(request.user, project_id, view_id, group_id, json.loads(request.body))
	return render_to_json("usergroup", Serializer().serialize(group))

@login_required
@require_http_methods(["PUT"])
@handle_http_errors
@handle_malformed
def addUserToGroup(request, project_id, view_id, group_id):
	group = authorization.views.addUserToGroup(request.user, project_id, view_id, group_id, json.loads(request.body))
	return render_to_json("usergroup", Serializer().serialize(group))

@login_required
@require_http_methods(["DELETE"])
@handle_http_errors
def removeUserFromGroup(request, project_id, view_id, group_id, user_id):
	authorization.views.removeUserFromGroup(request.user, project_id, view_id, group_id, user_id)
	return render_to_success("The user has been successfully removed from the group.")
