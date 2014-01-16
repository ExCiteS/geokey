from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from opencomap.libs.serializers import SingleSerializer, ObjectSerializer
from opencomap.libs.decorators import handle_http_errors

from opencomap.apps.backend.auth import projects as projectAuth
from oauth import oauthenticate

@oauthenticate
@require_http_methods(["GET"])
def project_list(request):
	projects = projectAuth.projects_list(request.user)
	serializer = ObjectSerializer()
	return HttpResponse('{ "projects": ' + serializer.serialize(projects) + "}")


@oauthenticate
@require_http_methods(["GET"])
@handle_http_errors
def project_single(request, project_id):
	project = projectAuth.project(request.user, project_id)
	serializer = SingleSerializer()
	return HttpResponse('{ "project": ' + serializer.serialize(project) + "}")