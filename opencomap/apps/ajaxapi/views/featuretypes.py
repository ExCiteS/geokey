from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from django.http import HttpResponse

import json

from opencomap.apps.backend import authorization
from opencomap.libs.serializers import FeatureTypeSerializer, FieldSerializer, ObjectSerializer
from opencomap.libs.decorators import handle_http_errors, handle_malformed

@login_required
@require_http_methods(["PUT"])
@handle_http_errors
@handle_malformed
def update(request, project_id, featuretype_id):
	featuretype = authorization.featuretypes.update(request.user, project_id, featuretype_id, json.loads(request.body))
	return HttpResponse('{ "featuretype": ' + FeatureTypeSerializer().serialize([featuretype]) + "}") 

@login_required
@require_http_methods(["PUT"])
@handle_http_errors
@handle_malformed
def updateField(request, project_id, featuretype_id, field_id):
	field = authorization.featuretypes.updateField(request.user, project_id, featuretype_id, field_id, json.loads(request.body))
	return HttpResponse('{ "field": ' + FieldSerializer().serialize([field]) + "}")

@login_required
@require_http_methods(["PUT"])
@handle_http_errors
@handle_malformed
def addLookupValue(request, project_id, featuretype_id, field_id):
	field = authorization.featuretypes.addLookupValue(request.user, project_id, featuretype_id, field_id, json.loads(request.body))
	return HttpResponse('{ "field": ' + FieldSerializer().serialize([field]) + "}")

@login_required
@require_http_methods(["DELETE"])
@handle_http_errors
@handle_malformed
def removeLookupValue(request, project_id, featuretype_id, field_id, lookup_id):
	field = authorization.featuretypes.removeLookupValue(request.user, project_id, featuretype_id, field_id, lookup_id)
	return HttpResponse('{ "field": ' + FieldSerializer().serialize([field]) + "}")