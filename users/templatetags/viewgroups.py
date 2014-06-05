from django import template

register = template.Library()


def get_view_group(view, group):
    return '<div class="list-group-item">\
            <div class="checkbox">\
                <label><input class="view-permission" name="view" value="%s" type="checkbox" %s> %s </label>\
            </div>\
        </div>' % (
        view.id,
        'checked' if group.viewgroups.filter(view=view).exists() else '',
        view.name
        )


@register.simple_tag
def viewgroups(group):
    html = ''
    for view in group.project.views.all():
        html += get_view_group(view, group)

    return html
