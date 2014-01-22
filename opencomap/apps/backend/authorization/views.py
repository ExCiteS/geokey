from decorators import check_admin

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