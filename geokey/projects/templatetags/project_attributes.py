"""Template tags for project attributes."""

from django import template
from django.template.loader import render_to_string


register = template.Library()


@register.simple_tag
def project_attributes(project):
    return render_to_string(
        'projects/project_attributes.html',
        {
            'creator': project.creator.display_name,
            'created_at': project.created_at.strftime("%d %B %Y, %H:%M"),
            'private_label': ('Private' if project.isprivate else 'Public'),
            'inactive': project.status == 'inactive'
        }
    )
