from django import template

register = template.Library()


@register.simple_tag
def is_in(value, key, d):
    if d is not None:
        if d.get(key) is not None:
            if str(value) in d[key]:
                return 'selected'

    return ''
