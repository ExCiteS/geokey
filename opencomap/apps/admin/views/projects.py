from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from opencomap.apps.backend import authorization
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.models.project import Project
import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.admin.libs.decorators import handle_errors, check_admin

@login_required
def createProject(request):
	if request.method == 'GET':
		return render(request, 'project.new.html', RequestContext(request))
	
	elif request.method == 'POST':
		private = request.POST.get('isprivate') == 'true'
		project = Factory.createProject(request.POST.get('name'), request.POST.get('description'), request.user, isprivate=private)
		return redirect('project_view', project.id)

@login_required
@handle_errors
def viewProject(request, project_id):
	project = authorization.projects.get_single(request.user, project_id)
	views = authorization.views.get_list(request.user, project_id)
	admin = project.admins.isMember(request.user)
	return render(request, 'project.html', RequestContext(request, {"project": project, "views": views, "admin": admin}))

@login_required
@handle_errors
@check_admin
def editProject(request, project_id, project=None):
	project = authorization.projects.get_single(request.user, project_id)
	return render(request, 'project.edit.html', RequestContext(request, {"project": project, "status_types": STATUS_TYPES}))