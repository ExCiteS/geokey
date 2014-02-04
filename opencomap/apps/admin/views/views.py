from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from opencomap.apps.admin.libs.decorators import handle_errors, check_admin
from opencomap.apps.backend import authorization

@login_required
@require_http_methods(["GET"])
@handle_errors
def viewView(request, project_id, view_id):
	view = authorization.views.get_single(request.user, project_id, view_id)
	admin = view.project.admins.isMember(request.user) or view.can_admin(request.user)
	return render(request, 'view.html', RequestContext(request, {"view": view, "admin": admin}))

@login_required
@require_http_methods(["GET", "POST"])
@handle_errors
def new(request, project_id):
	if request.method == "GET":
		project = authorization.projects.get_single(request.user, project_id)
		if project.admins.isMember(request.user):
			return render(request, 'view.new.html', RequestContext(request, {"project": project}))
		else:
			return render(request, 'error.html', RequestContext(request, {"error": "You are not member of the administrators group of this project and therefore not permitted to edit the project settings.", "head": "Permission denied."}))

	elif request.method == "POST":
		view = authorization.views.create(request.user, project_id, request.POST)
		return redirect('view_view', project.id, view.id)

@login_required
@require_http_methods(["GET"])
@handle_errors
def editView(request, project_id, view_id):
	view = authorization.views.get_single(request.user, project_id, view_id)
	return render(request, 'view.edit.html', RequestContext(request, {"view": view}))

@login_required
@require_http_methods(["GET", "POST"])
@handle_errors
def create_usergroup(request, project_id, view_id):
	view = authorization.views.get_single(request.user, project_id, view_id)
	if request.method == "GET":
		if view.project.admins.isMember(request.user) or view.can_admin(request.user):
			return render(request, 'view.group.new.html', RequestContext(request, {"view": view}))
		else:
			return render(request, 'error.html', RequestContext(request, {"error": "You are not member of the administrators group of this view or the project and therefore not permitted to edit the view settings.", "head": "Permission denied."}))

	if request.method == "POST":
		view = authorization.views.create_usergroup(request.user, project_id, view_id, request.POST)
		return redirect('view_settings', project_id, view_id)


@login_required
@require_http_methods(["GET"])
@handle_errors
def view_usergroup(request, project_id, view_id, group_id):
	group = authorization.views.get_usergroup(request.user, project_id, view_id, group_id)
	return render(request, 'view.group.html', RequestContext(request, {"group": group}))