from decorators import check_admin, check_view_admin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from opencomap.libs.exceptions import MalformedBody
from opencomap.apps.backend.models.view import View
from opencomap.apps.backend.models.viewgroup import ViewGroup
import projects

def get_list(user, project):
	result = []
	views = project.view_set.all()

	for view in views:
		if view.isViewable(user):
			result.append(view)

	return project, result

def get_single(user, project_id, view_id):
	project = projects.get_single(user, project_id)
	view = project.view_set.get(pk=view_id)
	if view.isViewable(user):
		return view
	else:
		raise PermissionDenied('You are not allowed to access this view.')

@check_admin
def create(user, project_id, data, project=None):
	view = View(name=data.get('name'), description=data.get('description'), project=project, creator=user)
	view.save()
	return view

@check_view_admin
def update(user, project_id, view_id, data, project=None, view=None):
	if data.get('description') != None: view.update(description=data.get('description'))
	return view

@check_view_admin
def delete(user, project_id, view_id, project=None, view=None):
	view.delete()
	return view

@check_view_admin
def create_usergroup(user, project_id, view_id, data, project=None, view=None):
	group = ViewGroup(name=data.get('name'), description=data.get('description'), view=view)
	group.save()
	return view

@check_view_admin
def get_usergroup(user, project_id, view_id, group_id, project=None, view=None):
	group = view.viewgroup_set.get(pk=group_id)
	return group

@check_view_admin
def update_usergrpup(user, project_id, view_id, group_id, data, project=None, view=None):
	group = view.viewgroup_set.get(pk=group_id)
	if data.get('description') != None: group.update(description=data.get('description'))
	if data.get('can_admin') != None: group.update(can_admin=data.get('can_admin'))
	if data.get('can_edit') != None: group.update(can_edit=data.get('can_edit'))
	if data.get('can_read') != None: group.update(can_read=data.get('can_read'))
	if data.get('can_view') != None: group.update(can_view=data.get('can_view'))

	return group

@check_view_admin
def addUserToGroup(user, project_id, view_id, group_id, userToAdd, project=None, view=None):
	print 'adduser'
	group = view.viewgroup_set.get(pk=group_id)
	try:
		user = User.objects.get(pk=userToAdd.get('userId'))
	except User.DoesNotExist, err:
		raise MalformedBody(err)
	group.addUsers(user)
	print group.users.all()

	return group

@check_view_admin
def removeUserFromGroup(user, project_id, view_id, group_id, userToRemove, project=None, view=None):
	group = view.viewgroup_set.get(pk=group_id)
	user = group.users.get(pk=userToRemove)

	group.removeUsers(user)
	return group