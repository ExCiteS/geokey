from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from opencomap.libs.exceptions import MalformedBody
from opencomap.apps.backend.models.view import View
from opencomap.apps.backend.models.viewgroup import ViewGroup
from decorators import check_admin

import projects


def get_list(user, project_id):
    """
    Return a list of all views of the given project, that are accessible to
    the user. The list may be empty if the user is not eligible to access any
    views.
    """
    result = []
    project = projects.get_single(user, project_id)
    views = project.view_set.all()

    for view in views:
        if view.isViewable(user):
            result.append(view)

    return result


def get_single(user, project_id, view_id):
    """
    Return a single view of the given project, or raises
    `PermissionDenied` if the user is eligible to access the view.
    """
    project = projects.get_single(user, project_id)
    view = project.view_set.get(pk=view_id)
    if view.isViewable(user):
        return view
    else:
        raise PermissionDenied('You are not allowed to access this view.')


@check_admin
def create(user, project_id, data, project=None):
    """
    Creates a new view for the given project, or raises `PermissionDenied` if
    the user is eligible to alter the project.
    """
    view = View(
        name=data.get('name'),
        description=data.get('description'),
        project=project,
        creator=user
    )
    view.save()
    return view


@check_admin
def update(user, project_id, view_id, data, project=None):
    """
    Updates the view for the given project, or raises `PermissionDenied` if
    the user is eligible to alter the project.
    """
    view = project.view_set.get(pk=view_id)
    if data.get('description') is not None:
        view.update(description=data.get('description'))
    return view


@check_admin
def delete(user, project_id, view_id, project=None):
    """
    Deletes the view for the given project, or raises `PermissionDenied` if
    the user is eligible to alter the project.
    """
    view = project.view_set.get(pk=view_id)
    view.delete()
    return view


@check_admin
def create_usergroup(user, project_id, view_id, data, project=None):
    """
    Creates a new user grpup the view for the given project and view, or
    raises `PermissionDenied` if the user is eligible to alter the project.
    """
    view = project.view_set.get(pk=view_id)
    group = ViewGroup(
        name=data.get('name'),
        description=data.get('description'),
        view=view
    )
    group.save()
    return view


@check_admin
def get_usergroup(user, project_id, view_id, group_id, project=None):
    """
    Returns a new user grpup the view for the given project and view, or
    raises `PermissionDenied` if the user is eligible to alter the project.
    """
    view = project.view_set.get(pk=view_id)
    group = view.viewgroup_set.get(pk=group_id)
    return group


@check_admin
def update_usergrpup(user, project_id, view_id, group_id, data, project=None):
    """
    Updates new user group of the view for the given project and view, or
    raises `PermissionDenied` if the user is eligible to alter the project.
    """
    view = project.view_set.get(pk=view_id)
    group = view.viewgroup_set.get(pk=group_id)
    if data.get('description') is not None:
        group.update(description=data.get('description'))
    if data.get('can_edit') is not None:
        group.update(can_edit=data.get('can_edit'))
    if data.get('can_read') is not None:
        group.update(can_read=data.get('can_read'))
    if data.get('can_view') is not None:
        group.update(can_view=data.get('can_view'))

    return group


@check_admin
def add_user_to_group(user, project_id, view_id, group_id, userToAdd,
                      project=None):
    """
    Adds a user to the user grpup of the view for the given project and view,
    or raises `PermissionDenied` if the user is eligible to alter the project.
    """
    view = project.view_set.get(pk=view_id)
    group = view.viewgroup_set.get(pk=group_id)
    try:
        user = User.objects.get(pk=userToAdd.get('userId'))
    except User.DoesNotExist, err:
        raise MalformedBody(err)
    group.addUsers(user)

    return group


@check_admin
def remove_user_from_group(user, project_id, view_id, group_id, userToRemove,
                           project=None):
    """
    Removes a user from the user grpup of the view for the given project and
    view, or raises `PermissionDenied` if the user is eligible to alter the
    project.
    """
    view = project.view_set.get(pk=view_id)
    group = view.viewgroup_set.get(pk=group_id)
    user = group.users.get(pk=userToRemove)

    group.removeUsers(user)
    return group
