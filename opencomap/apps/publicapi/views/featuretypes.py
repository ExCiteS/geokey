from django.views.decorators.http import require_http_methods

from opencomap.libs.serializers import ObjectSerializer
from opencomap.libs.views import render_to_json
from opencomap.libs.decorators.http import handle_http_errors
from opencomap.libs.oauth import oauthenticate

from opencomap.apps.backend import authorization

@oauthenticate
@require_http_methods(["GET"])
@handle_http_errors
def featuretype_list(request, project_id):
	featuretypes = authorization.featuretypes.get_list(request.user, project_id)
	return render_to_json("featuretypes", ObjectSerializer().serialize(featuretypes))