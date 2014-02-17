from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import json

from opencomap.libs.serializers import ObjectSerializer as Serializer
from opencomap.libs.decorators.http import handle_http_errors, handle_malformed
from opencomap.libs.views import render_to_json, render_to_success

from backend import authorization


@login_required
@require_http_methods(["PUT", "DELETE"])
@handle_http_errors
@handle_malformed
def update(request, project_id):
    if request.method == "PUT":
        project = authorization.projects.update(
            request.user,
            project_id,
            json.loads(request.body)
        )
        return render_to_json("project", Serializer().serialize(project))

    elif request.method == "DELETE":
        project = authorization.projects.delete(request.user, project_id)
        return render_to_success('The project has been deleted.')


@login_required
@require_http_methods(["PUT"])
@handle_malformed
@handle_http_errors
def add_user_to_group(request, project_id, group_id):
    group = authorization.projects.add_user_to_group(
        request.user,
        project_id,
        group_id,
        json.loads(request.body)
    )
    return render_to_json("usergroup", Serializer().serialize(group))


@login_required
@require_http_methods(["DELETE"])
@handle_http_errors
def remove_user_from_group(request, project_id, group_id, user_id):
    authorization.projects.remove_user_from_group(
        request.user,
        project_id,
        group_id,
        user_id
    )
    return render_to_success(
        'The user has been successfully removed from the group.'
    )
