from django import template
from django.core.urlresolvers import reverse

register = template.Library()


def get_view_group(view, group):
    disabled = ''
    message = ''
    if not view.project.isprivate and not view.isprivate:
        disabled = 'disabled="disabled"'
        message = '<p class="text-danger">This data grouping is public. To restrict access, navigate to the <a href="%s">data grouping settings</a> and revoke access from the public.</p>' % reverse('admin:grouping_permissions', kwargs={'project_id' :view.project.id, 'grouping_id' : view.id, })

    if group.viewgroups.filter(view=view).exists():
        return '<div class="overview-list-item">\
                    %s<button type="button" name="%s" class="btn btn-default pull-right active grant-single" data-toggle="button" %s><span class="text-danger">Revoke access</span></button><strong>%s</strong><p>%s</p>\
                </div>' % (
            message,
            view.id,
            disabled,
            view.name,
            view.description
        )
    else:
        return '<div class="overview-list-item">\
                    %s<button type="button" name="%s" class="btn btn-default pull-right grant-single" data-toggle="button" %s><span class="text-success">Grant access</span></button><strong>%s</strong><p>%s</p>\
                </div>' % (
            message,
            view.id,
            disabled,
            view.name,
            view.description
        )


@register.simple_tag
def viewgroups(group):
    html = ''
    for view in group.project.views.all():
        html += get_view_group(view, group)

    return html
