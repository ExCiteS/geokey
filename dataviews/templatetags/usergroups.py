from django import template

register = template.Library()


def get_user_group(group, view):
    disabled = ''
    if not view.project.isprivate and not view.isprivate:
        disabled = 'disabled="disabled"'

    if view.usergroups.filter(usergroup=group).exists():
        html = '<div class="overview-list-item">\
                    <button type="button" name="%s" class="btn btn-default pull-right active grant-single" data-toggle="button" %s><span class="text-danger">Revoke access</span></button><strong>%s</strong><p>%s</p>\
                </div>' % (
            group.id,
            disabled,
            group.name,
            group.description
        )
    else:
        html = '<div class="overview-list-item">\
                    <button type="button" name="%s" class="btn btn-default pull-right grant-single" data-toggle="button" %s><span class="text-success">Grant access</span></button><strong>%s</strong><p>%s</p>\
                </div>' % (
            group.id,
            disabled,
            group.name,
            group.description
        )

    return html


@register.simple_tag
def usergroups(view):
    html = ''
    for group in view.project.usergroups.all():
        html += get_user_group(group, view)

    return html
