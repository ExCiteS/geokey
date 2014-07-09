from django import template

register = template.Library()


def get_user_group(group, view):
    html = '<li class="list-group-item">\
                <div class="checkbox">\
                    <label>\
                        <input type="checkbox" name="usergroup" value="%s" %s> %s\
                    </label>\
                </div>\
            </li>' % (
        group.id,
        'checked' if view.usergroups.filter(usergroup=group).exists() else '',
        group.name
    )

    return html


@register.simple_tag
def usergroups(view):
    html = ''
    for group in view.project.usergroups.all():
        html += get_user_group(group, view)

    return html
