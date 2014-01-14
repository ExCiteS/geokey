from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.core.exceptions import PermissionDenied

import json

from opencomap.apps.backend.serializers import SingleSerializer
from opencomap.apps.backend.serializers import ObjectSerializer

from opencomap.apps.backend.auth import projects as projectAuth
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.usergroup import UserGroup

@login_required
def listProjects(request):
	if request.method == "GET":
		projects = projectAuth.projects_list(request.user)
		serializer = ObjectSerializer()
		return HttpResponse('{ "projects": ' + serializer.serialize(projects) + "}")
	else:
		return HttpResponse("The HTTP method used is not allowed with this ressource", status=405)

@login_required
def singleProject(request, project_id):
	if request.method == "GET":
		try:
			project = projectAuth.project(request.user, project_id)
			serializer = SingleSerializer()
			return HttpResponse('{ "project": ' + serializer.serialize(project) + "}")
		except PermissionDenied, err:
			return HttpResponse(err, status=401)
		except Project.DoesNotExist, err:
			return HttpResponse(err, status=404)
	else:
		return HttpResponse("The HTTP method used is not allowed with this ressource", status=405)