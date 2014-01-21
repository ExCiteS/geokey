from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from opencomap.libs.serializers import ObjectSerializer as Serializer
from opencomap.libs.decorators import handle_http_errors
from opencomap.libs.oauth import oauthenticate 

from opencomap.apps.backend import authorization


@oauthenticate
@require_http_methods(["GET"])
def project_list(request):
	projects = authorization.projects.projects_list(request.user)
	return HttpResponse('{ "projects": ' + Serializer().serialize(projects) + "}")


@oauthenticate
@require_http_methods(["GET"])
@handle_http_errors
def project_single(request, project_id):
	project = authorization.projects.project(request.user, project_id)
	return HttpResponse('{ "project": ' + Serializer().serialize(project) + "}")