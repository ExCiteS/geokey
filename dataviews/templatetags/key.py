import json
from django import template

register = template.Library()


@register.filter(name='key')
def key(d, key_name):
    if key_name in d:
        return 'value=%s' % d[key_name]

    return ''


@register.filter(name='minval')
def minval(d, key_name):
    if d.get(key_name) is not None:
        minval = json.loads(d.get(key_name)).get('minval')
        if minval is not None:
            return 'value=%s' % minval

    return ''


@register.filter(name='maxval')
def maxval(d, key_name):
    if d.get(key_name) is not None:
        maxval = json.loads(d.get(key_name)).get('maxval')
        if maxval is not None:
            return 'value=%s' % maxval

    return ''
