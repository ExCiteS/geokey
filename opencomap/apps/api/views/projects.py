from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.core.exceptions import PermissionDenied

from opencomap.apps.api.serializers import SingleSerializer

from opencomap.apps.backend import views as view
from opencomap.apps.backend.models.choice import STATUS_TYPES

@login_required
def updateProject(request, project_id):
	print request.POST
	try: 
		project = view.updateProject(request.user, project_id, request.POST)
		serializer = SingleSerializer()
		return HttpResponse(serializer.serialize(project))
	except PermissionDenied, err:
		return HttpResponse(err, status=401)

@login_required
def deleteProject(request, project_id):
	try: 
		project = view.deleteProject(request.user, project_id)
		return HttpResponse("The project has been deleted.")
	except PermissionDenied, err:
		return HttpResponse(err, status=401)