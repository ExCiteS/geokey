from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from opencomap.apps.backend import authorization
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.models.project import Project
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
		project = authorization.projects.project(request.user, project_id)
		admin = project.admins.isMember(request.user)
		return render(request, 'project.html', RequestContext(request, {"project": project, "admin": admin}))
	except Project.DoesNotExist, err:
		return render(request, 'project.html', RequestContext(request, {"error": err}))

@login_required
def editProject(request, project_id):
	try:
		project = authorization.projects.project(request.user, project_id)
		if project.admins.isMember(request.user):
			return render(request, 'project.edit.html', RequestContext(request, {"project": project, "status_types": STATUS_TYPES}))
		else:
			return render(request, 'project.edit.html', RequestContext(request, {"error": "You are not allowed to edit the setting of this project"}))	
	except Project.DoesNotExist, err:
		return render(request, 'project.edit.html', RequestContext(request, {"error": err}))