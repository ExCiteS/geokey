from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from opencomap.libs.serializers import ObjectSerializer
from opencomap.libs.decorators import handle_http_errors

from opencomap.apps.backend.auth import projects as projectAuth
from oauth import oauthenticate

@oauthenticate
@require_http_methods(["GET"])
@handle_http_errors
def featuretype_list(request, project_id):
	project = projectAuth.project(request.user, project_id)
	serializer = ObjectSerializer()
	return HttpResponse('{ "featuretypes": ' + serializer.serialize(project.getFeatureTypes()) + "}")