from django import template

from users.models import ViewUserGroup

register = template.Library()


def get_view_group(view, group):
    try:
        view_group = group.viewgroups.get(view=view)

        return '<tr data-view-id="%s">\
            <td><input type="checkbox" name="active" checked="true"></td>\
            <td>%s</td>\
            <td><input type="checkbox" name="can_view" %s></td>\
            <td><input type="checkbox" name="can_read" %s></td>\
            <td><input type="checkbox" name="can_moderate" %s></td>\
        </tr>' % (
            view.id,
            view.name,
            'checked' if view_group.can_view else '',
            'checked' if view_group.can_read else '',
            'checked' if view_group.can_moderate else '')
    except ViewUserGroup.DoesNotExist:
        return '<tr data-view-id="%s">\
            <td><input type="checkbox" name="active"></td>\
            <td>%s</td>\
            <td><input type="checkbox" name="can_view" checked="true" disabled="true"></td>\
            <td><input type="checkbox" name="can_read" disabled="true"></td>\
            <td><input type="checkbox" name="can_moderate" disabled="true"></td>\
        </tr>' % (view.id, view.name)


@register.simple_tag
def viewgroups(group):
    html = ''
    for view in group.project.views.all():
        html += get_view_group(view, group)

    return html
