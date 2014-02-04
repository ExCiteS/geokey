from opencomap.apps.backend.models.project import Project
from django.core.exceptions import PermissionDenied

def check_admin(func):
	def wrapped(*args, **kwargs):
		project = Project.objects.get(pk=args[1])
		if project.admins.isMember(args[0]):
			return func(project=project, *args, **kwargs)
		else:
			raise PermissionDenied('You are not allowed to alter the settings of this project.')

	return wrapped