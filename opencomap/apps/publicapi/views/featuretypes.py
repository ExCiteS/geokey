from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from opencomap.libs.serializers import FeatureTypeSerializer
from opencomap.libs.decorators import handle_http_errors
from opencomap.libs.oauth import oauthenticate

from opencomap.apps.backend import authorization

@oauthenticate
@require_http_methods(["GET"])
@handle_http_errors
def featuretype_list(request, project_id):
	project = authorization.projects.project(request.user, project_id)
	return HttpResponse('{ "featuretypes": ' + FeatureTypeSerializer().serialize(project.getFeatureTypes()) + "}")