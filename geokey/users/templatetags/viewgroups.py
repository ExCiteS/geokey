from django import template
from django.core.urlresolvers import reverse

register = template.Library()


def get_view_group(grouping, group):
    disabled = ''
    message = ''
    if not grouping.project.isprivate and not grouping.isprivate:
        disabled = 'disabled="disabled"'
        message = '<p class="text-danger">This data grouping is public. To \
            restrict access, navigate to the <a href="%s">data grouping \
            settings</a> and revoke access from the public.</p>' % reverse(
                'admin:grouping_permissions',
                kwargs={
                    'project_id': grouping.project.id,
                    'grouping_id': grouping.id
                }
            )

    if group.viewgroups.filter(grouping=grouping).exists():
        return ('<li>'
                '%s<button type="button" name="%s" class="btn btn-default '
                'pull-right active grant-single" data-toggle="button" %s>'
                '<span class="text-danger">Revoke access</span></button>'
                '<strong>%s</strong><p>%s</p>'
                '</li>' % (
                    message,
                    grouping.id,
                    disabled,
                    grouping.name,
                    grouping.description)
                )
    else:
        return ('<li>'
                '%s<button type="button" name="%s" class="btn btn-default '
                'pull-right grant-single" data-toggle="button" %s><span '
                'class="text-success">Grant access</span></button>'
                '<strong>%s</strong><p>%s</p>'
                '</li>' % (
                    message,
                    grouping.id,
                    disabled,
                    grouping.name,
                    grouping.description)
                )


@register.simple_tag
def viewgroups(group):
    html = '<ul class="list-unstyled overview-list">'
    for grouping in group.project.groupings.all():
        html += get_view_group(grouping, group)

    html += '</ul>'

    return html
