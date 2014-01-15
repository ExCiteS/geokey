from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

import json

from opencomap.libs.serializers import SingleSerializer, ObjectSerializer
from opencomap.libs.decorators import handle_http_errors

from opencomap.apps.backend.auth import projects as projectAuth
from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.usergroup import UserGroup

@login_required
@require_http_methods(["GET"])
def listProjects(request):
	projects = projectAuth.projects_list(request.user)
	serializer = ObjectSerializer()
	return HttpResponse('{ "projects": ' + serializer.serialize(projects) + "}")


@login_required
@require_http_methods(["GET"])
@handle_http_errors
def singleProject(request, project_id):
	project = projectAuth.project(request.user, project_id)
	serializer = SingleSerializer()
	return HttpResponse('{ "project": ' + serializer.serialize(project) + "}")