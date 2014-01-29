from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.template import RequestContext

from opencomap.apps.backend import authorization
import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.featuretype import FeatureType
from opencomap.apps.backend.models.choice import STATUS_TYPES

@login_required
@require_http_methods(["GET", "POST"])
def createFeaturetype(request, project_id):
	project = authorization.projects.project(request.user, project_id)

	if request.method == "GET":
		return render(request, 'featuretype.new.html', RequestContext(request, {"project": project}))

	if request.method == "POST":
		featuretype = Factory.createFeaturetype(request.POST.get('name'), request.POST.get('description'), request.user, project)
		return redirect('featuretype_view', project.id, featuretype.id)

@login_required
@require_http_methods(["GET"])
def viewFeaturetype(request, project_id, featuretype_id):
	try:
		project = authorization.projects.project(request.user, project_id)
		admin = project.admins.isMember(request.user)
		featuretype = project.featuretype_set.get(pk=featuretype_id)

		return render(request, 'featuretype.html', RequestContext(request, {"project": project, "featuretype": featuretype, "admin": admin, "status_types": STATUS_TYPES}))
	except (Project.DoesNotExist, FeatureType.DoesNotExist) as err:
		return render(request, 'featuretype.html', RequestContext(request, {"error": err}))
	