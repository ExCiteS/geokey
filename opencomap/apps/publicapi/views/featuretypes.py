from django.views.decorators.http import require_http_methods

from opencomap.libs.serializers import FeatureTypeSerializer
from opencomap.libs.views import render_to_json
from opencomap.libs.decorators.http import handle_http_errors
from opencomap.libs.oauth import oauthenticate

from opencomap.apps.backend import authorization

@oauthenticate
@require_http_methods(["GET"])
@handle_http_errors
def featuretype_list(request, project_id):
	project = authorization.projects.project(request.user, project_id)
	return render_to_json("featuretypes", FeatureTypeSerializer().serialize(project.getFeatureTypes()))