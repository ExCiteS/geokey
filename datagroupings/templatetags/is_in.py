import json
from django import template

register = template.Library()


@register.simple_tag
def is_in(value, key, d):
    if d.get(key) is not None:
        l = json.loads(d[key])
        if str(value) in l:
            return 'selected'

    return ''
