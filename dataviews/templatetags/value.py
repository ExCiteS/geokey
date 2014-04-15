import iso8601
import moment

from django import template

register = template.Library()


@register.simple_tag
def value(attributes, field):
    value = attributes.get(field.key)

    if value is None:
        return '&mdash;'

    if field.fieldtype == 'LookupField':
        for lookup in field.lookupvalues:
            if lookup.id == value:
                return lookup.name

    if field.fieldtype == 'DateTimeField':
        return moment.date(iso8601.parse_date(value)).format('YYYY-M-D h:m A')

    return value
