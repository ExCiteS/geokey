import json
from django import template

register = template.Library()


@register.simple_tag
def is_in(value, key, d):
    l = json.loads(d[key])
    if str(value) in l:
        return 'selected'
    else:
        return ''
