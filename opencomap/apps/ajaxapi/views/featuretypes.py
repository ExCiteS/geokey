from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import json

from opencomap.apps.backend import authorization
from opencomap.libs.serializers import ObjectSerializer
from opencomap.libs.decorators.http import handle_http_errors, handle_malformed
from opencomap.libs.views import render_to_json


@login_required
@require_http_methods(["PUT"])
@handle_http_errors
@handle_malformed
def update(request, project_id, featuretype_id):
    featuretype = authorization.featuretypes.update(
        request.user,
        project_id,
        featuretype_id,
        json.loads(request.body)
    )
    return render_to_json(
        "featuretype",
        ObjectSerializer().serialize(featuretype)
    )


@login_required
@require_http_methods(["PUT"])
@handle_http_errors
@handle_malformed
def update_field(request, project_id, featuretype_id, field_id):
    field = authorization.featuretypes.update_field(
        request.user,
        project_id,
        featuretype_id,
        field_id,
        json.loads(request.body)
    )
    return render_to_json("field", ObjectSerializer().serialize(field))


@login_required
@require_http_methods(["PUT"])
@handle_http_errors
@handle_malformed
def add_lookup_value(request, project_id, featuretype_id, field_id):
    field = authorization.featuretypes.add_lookup_value(
        request.user,
        project_id,
        featuretype_id,
        field_id,
        json.loads(request.body)
    )
    return render_to_json("field", ObjectSerializer().serialize(field))


@login_required
@require_http_methods(["DELETE"])
@handle_http_errors
@handle_malformed
def remove_lookup_value(request, project_id, featuretype_id, field_id,
                        lookup_id):
    field = authorization.featuretypes.remove_lookup_value(
        request.user,
        project_id,
        featuretype_id,
        field_id,
        lookup_id
    )
    return render_to_json("field", ObjectSerializer().serialize(field))
