import json
from django import template

register = template.Library()


@register.filter(name='key')
def key(d, key_name):
    return d[key_name]


@register.filter(name='minval')
def minval(d, key_name):
    minval = json.loads(d[key_name])['minval']
    if minval is not None:
        return 'value=%s' % minval
    else:
        return ''


@register.filter(name='maxval')
def maxval(d, key_name):
    maxval = json.loads(d[key_name])['maxval']
    if minval is not None:
        return 'value=%s' % maxval
    else:
        return ''
