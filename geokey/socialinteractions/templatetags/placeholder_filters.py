"""Custom placeholder template filters"""

from django import template

register = template.Library()


@register.filter()
def project_replace(value, project_name):
    return value.replace('$project$', hashify(project_name))


@register.filter()
def hashify(value):
    return "#" + value.replace(' ', '').lower()
