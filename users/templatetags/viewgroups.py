from django import template

register = template.Library()


def get_view_group(view, group):
    if group.viewgroups.filter(view=view).exists():
        return '<div class="overview-list-item">\
                    <button type="button" name="%s" class="btn btn-default pull-right active grant-single" data-toggle="button"><span class="text-danger">Revoke access</span></button><strong>%s</strong><p>%s</p>\
                </div>' % (
            view.id,
            view.name,
            view.description
        )
    else:
        return '<div class="overview-list-item">\
                    <button type="button" name="%s" class="btn btn-default pull-right grant-single" data-toggle="button"><span class="text-success">Grant access</span></button><strong>%s</strong><p>%s</p>\
                </div>' % (
            view.id,
            view.name,
            view.description
        )


@register.simple_tag
def viewgroups(group):
    html = ''
    for view in group.project.views.all():
        html += get_view_group(view, group)

    return html
