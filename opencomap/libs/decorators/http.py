from django.core.exceptions import PermissionDenied, ValidationError
from opencomap.libs.exceptions import MalformedBody
from opencomap.libs.views import render_to_error

from django.contrib.auth.models import User
from opencomap.apps.backend.models import Project
from opencomap.apps.backend.models import FeatureType, Field, LookupValue
from opencomap.apps.backend.models import UserGroup
from opencomap.apps.backend.models import View

def handle_http_errors(func):
	def wrapped(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except PermissionDenied, err:
			return render_to_error(401, err)
		except (User.DoesNotExist, Project.DoesNotExist, FeatureType.DoesNotExist, Field.DoesNotExist, LookupValue.DoesNotExist, UserGroup.DoesNotExist, View.DoesNotExist) as err:
			return render_to_error(404, err)
	
	return wrapped

def handle_malformed(func):
	def wrapped(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except (MalformedBody, ValidationError) as err:
			return render_to_error(400, err)
		except AttributeError, err:
			return render_to_error(404, err)
	
	return wrapped