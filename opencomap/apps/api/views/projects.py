from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from opencomap.apps.api.serializers import SingleSerializer

from opencomap.apps.backend import views as view

@login_required
def updateProject(request, project_id):
    project = view.updateProject(request.user, project_id, request.POST)
    serializer = SingleSerializer()

    return HttpResponse(serializer.serialize(project))