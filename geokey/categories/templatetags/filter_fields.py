"""Template tags for filtering fields."""

from django import template


register = template.Library()


@register.filter
def only_fields(fields, type_name):
    return [field for field in fields if field.type_name == type_name]


@register.filter
def except_fields(fields, type_name):
    return [field for field in fields if field.type_name != type_name]
