from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.template import RequestContext

from opencomap.apps.backend import authorization
import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.featuretype import FeatureType, Field
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.models.FeatureType import FIELD_TYPES
from opencomap.apps.admin.libs.decorators import handle_errors, check_admin

@login_required
@require_http_methods(["GET", "POST"])
@handle_errors
def createFeaturetype(request, project_id):
	if request.method == "GET":
		project = authorization.projects.get_single(request.user, project_id)
		if project.admins.isMember(request.user):
			return render(request, 'featuretype.new.html', RequestContext(request, {"project": project}))
		else:
			return render(request, 'error.html', RequestContext(request, {"error": "You are not member of the administrators group of this project and therefore not permitted to edit the project settings.", "head": "Permission denied."}))
		

	if request.method == "POST":
		featuretype = authorization.featuretypes.create(request.user, project_id, request.POST)
		return redirect('featuretype_view', featuretype.project.id, featuretype.id)

@login_required
@require_http_methods(["GET"])
@handle_errors
def viewFeaturetype(request, project_id, featuretype_id):
	featuretype = authorization.featuretypes.get_single(request.user, project_id, featuretype_id)
	admin = featuretype.project.admins.isMember(request.user)
	return render(request, 'featuretype.html', RequestContext(request, {"featuretype": featuretype, "admin": admin, "status_types": STATUS_TYPES}))


@login_required
@require_http_methods(["GET", "POST"])
@handle_errors
def createField(request, project_id, featuretype_id):
	if request.method == "GET":
		featuretype = authorization.featuretypes.get_single(request.user, project_id, featuretype_id)
		if featuretype.project.admins.isMember(request.user):
			return render(request, 'field.new.html', RequestContext(request, {"featuretype": featuretype, "fieldtypes": FIELD_TYPES}))
		else:
			return render(request, 'error.html', RequestContext(request, {"error": "You are not member of the administrators group of this project and therefore not permitted to edit the project settings.", "head": "Permission denied."}))

	if request.method == "POST":
		field = authorization.featuretypes.createField(request.user, project_id, featuretype_id, request.POST)
		return redirect('field_view', field.featuretype.project.id, field.featuretype.id, field.id)

@login_required
@require_http_methods(["GET"])
@handle_errors
def viewField(request, project_id, featuretype_id, field_id):
	field = authorization.featuretypes.get_single_field(request.user, project_id, featuretype_id, field_id)
	if field.featuretype.project.admins.isMember(request.user):
		return render(request, 'field.html', RequestContext(request, {"field": field, "status_types": STATUS_TYPES}))
	else:
		return render(request, 'error.html', RequestContext(request, {"error": "You are not member of the administrators group of this project and therefore not permitted to edit the project settings.", "head": "Permission denied."}))