from django.views.decorators.http import require_http_methods

from opencomap.libs.serializers import ObjectSerializer as Serializer
from opencomap.libs.views import render_to_json
from opencomap.libs.decorators.http import handle_http_errors
from opencomap.libs.oauth import oauthenticate
from opencomap.apps.backend import authorization


@oauthenticate
@require_http_methods(["GET"])
def project_list(request):
    projects = authorization.projects.get_list(request.user)
    return render_to_json("projects", Serializer().serialize(projects))


@oauthenticate
@require_http_methods(["GET"])
@handle_http_errors
def project_single(request, project_id):
    project = authorization.projects.get_single(request.user, project_id)
    return render_to_json("project", Serializer().serialize(project))
