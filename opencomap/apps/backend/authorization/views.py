from decorators import check_admin
from django.contrib.auth.models import User
from opencomap.libs.exceptions import MalformedBody

@check_admin
def update(user, project_id, view_id, data, project=None):
	view = project.view_set.get(pk=view_id)
	if data.get('description') != None: view.update(description=data.get('description'))
	return view

@check_admin
def delete(user, project_id, view_id, project=None):
	view = project.view_set.get(pk=view_id)
	view.delete()
	return view

@check_admin
def addUserToGroup(user, project_id, view_id, group_id, userToAdd, project=None):
	group = project.view_set.get(pk=view_id).viewgroup_set.get(pk=group_id)
	try:
		user = User.objects.get(pk=userToAdd.get('userId'))
	except User.DoesNotExist, err:
		raise MalformedBody(err)
	group.addUsers(user)

	return group

@check_admin
def removeUserFromGroup(user, project_id, view_id, group_id, userToRemove, project=None):
	group = project.view_set.get(pk=view_id).viewgroup_set.get(pk=group_id)
	user = group.users.get(pk=userToRemove)

	group.removeUsers(user)
	return group