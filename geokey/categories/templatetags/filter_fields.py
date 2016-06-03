"""Template tags for filtering fields."""

from django import template


register = template.Library()


@register.filter
def only_fields(fields, type_names):
    type_names = [type_name.strip() for type_name in type_names.split(',')]
    return [field for field in fields if field.type_name in type_names]


@register.filter
def except_fields(fields, type_names):
    type_names = [type_name.strip() for type_name in type_names.split(',')]
    return [field for field in fields if field.type_name not in type_names]
