"""Custom placeholder template filters"""

from django import template

register = template.Library()


@register.filter()
def project_replace(value, project_name):
    return value.replace('$project$', project_name)
