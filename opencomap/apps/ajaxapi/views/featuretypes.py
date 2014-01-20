from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from django.http import HttpResponse

import json

from opencomap.apps.backend import authorization
from opencomap.libs.serializers import FeatureTypeSerializer
from opencomap.libs.decorators import handle_http_errors, handle_malformed

@login_required
@require_http_methods(["PUT", "DELETE"])
@handle_http_errors
@handle_malformed
def update(request, project_id, featuretype_id):
	if request.method == "PUT":
		featuretype = authorization.featuretypes.update(request.user, project_id, featuretype_id, json.loads(request.body))
		return HttpResponse('{ "featuretype": ' + FeatureTypeSerializer().serialize([featuretype]) + "}") 

	elif request.method == "DELETE":
		featuretype = authorization.featuretypes.delete(request.user, project_id, featuretype_id)
		return HttpResponse("The feature type has been deleted.")