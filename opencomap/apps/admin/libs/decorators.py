from django.core.exceptions import PermissionDenied
from opencomap.apps.backend.models import Project
from opencomap.apps.backend.models.view import View
from opencomap.apps.backend.models.featuretype import FeatureType, Field

from django.shortcuts import render
from django.template import RequestContext

def check_admin(func):
    def wrapped(*args, **kwargs):
        project = Project.objects.get(pk=kwargs.get('project_id'))
        if project.admins.isMember(args[0].user):
            return func(*args, **kwargs)
        else:
            raise PermissionDenied('You are not member of the administrators group of this project and therefore not permitted to edit the project settings.')

    return wrapped

def handle_errors(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionDenied, error:
            return render(args[0], 'error.html', RequestContext(args[0], {"error": str(error), "head": "Permission denied."}))
        except (Project.DoesNotExist, FeatureType.DoesNotExist, Field.DoesNotExist, View.DoesNotExist) as error:
            return render(args[0], 'error.html', RequestContext(args[0], {"error": str(error), "head": "Not found."}))
    return wrapped
