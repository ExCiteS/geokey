from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.core.exceptions import ObjectDoesNotExist

from opencomap.apps.api.serializers import SingleSerializer
from opencomap.apps.backend import views as view
import opencomap.apps.backend.models.factory as Factory

@login_required
def createProject(request):
    if request.method == 'GET':
        return render(request, 'project.new.html', RequestContext(request))
    
    elif request.method == 'POST':
        private = request.POST.get('isprivate') == 'true'
        Factory.createProject(request.POST.get('name'), request.POST.get('description'), request.user, isprivate=private).save()
        return redirect('/admin/dashboard')

@login_required
def viewProject(request, project_id):
	try:
		project = view.projects.project(request.user, project_id)
		admin = project.admins.isMember(request.user)
		return render(request, 'project.html', RequestContext(request, {"project": project, "admin": admin}))
	except ObjectDoesNotExist, err:
		return render(request, 'project.html', RequestContext(request, {"error": err}))

@login_required
def editProject(request, project_id):
	try:
		project = view.projects.project(request.user, project_id)
		if project.admins.isMember(request.user):
			return render(request, 'project.edit.html', RequestContext(request, {"project": view.projects.project(request.user, project_id)}))
		else:
			return render(request, 'project.edit.html', RequestContext(request, {"error": "You are not allowed to edit the setting of this project"}))	
	except ObjectDoesNotExist, err:
		return render(request, 'project.edit.html', RequestContext(request, {"error": err}))