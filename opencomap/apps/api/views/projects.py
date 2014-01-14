from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.core.exceptions import PermissionDenied

import json

from opencomap.apps.api.serializers import SingleSerializer
from opencomap.apps.api.serializers import ObjectSerializer

from opencomap.apps.backend.auth import projects as projectAuth
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.usergroup import UserGroup

@login_required
def updateProject(request, project_id):
	if request.method == "PUT":
		try: 
			project = projectAuth.updateProject(request.user, project_id, json.loads(request.body))
			serializer = SingleSerializer()
			return HttpResponse(serializer.serialize(project))
		except PermissionDenied, err:
			return HttpResponse(err, status=401)
		except Project.DoesNotExist, err:
			return HttpResponse(err, status=404)

	elif request.method == "DELETE":
		try: 
			project = projectAuth.deleteProject(request.user, project_id)
			return HttpResponse("The project has been deleted.")
		except PermissionDenied, err:
			return HttpResponse(err, status=401)
		except Project.DoesNotExist, err:
			return HttpResponse(err, status=404)
	else:
		return HttpResponse("The HTTP method used is not allowed with this ressource", status=405)

@login_required
def addUserToGroup(request, project_id, group_id):
	if request.method == "PUT":
		try: 
			group = projectAuth.addUserToGroup(request.user, project_id, group_id, json.loads(request.body))
			serializer = SingleSerializer()
			return HttpResponse(serializer.serialize(group))
		except PermissionDenied, err:
			return HttpResponse(err, status=401)
		except User.DoesNotExist, err:
			return HttpResponse(err, status=400)
		except Project.DoesNotExist, err:
			return HttpResponse(err, status=404)
		except UserGroup.DoesNotExist, err:
			return HttpResponse(err, status=404)
	else:
		return HttpResponse("The HTTP method used is not allowed with this ressource", status=405)

@login_required
def removeUserFromGroup(request, project_id, group_id, user_id):
	if request.method == "DELETE":
		try:
			projectAuth.removeUserFromGroup(request.user, project_id, group_id, user_id)
			return HttpResponse("The user has been successfully removed from the group.")
		except PermissionDenied, err:
			return HttpResponse(err, status=401)
		except User.DoesNotExist, err:
			return HttpResponse(err, status=404)
		except Project.DoesNotExist, err:
			return HttpResponse(err, status=404)
		except UserGroup.DoesNotExist, err:
			return HttpResponse(err, status=404)
	else:
		return HttpResponse("The HTTP method used is not allowed with this ressource", status=405)

@login_required
def listProjects(request):
	if request.method == "GET":
		projects = projectAuth.projects_list(request.user)
		serializer = ObjectSerializer()
		return HttpResponse(serializer.serialize(projects))
	else:
		return HttpResponse("The HTTP method used is not allowed with this ressource", status=405)

@login_required
def singleProject(request, project_id):
	if request.method == "GET":
		try:
			project = projectAuth.project(request.user, project_id)
			serializer = SingleSerializer()
			return HttpResponse(serializer.serialize(project))
		except PermissionDenied, err:
			return HttpResponse(err, status=401)
		except Project.DoesNotExist, err:
			return HttpResponse(err, status=404)
	else:
		return HttpResponse("The HTTP method used is not allowed with this ressource", status=405)