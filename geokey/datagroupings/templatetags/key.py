# import json
from django import template

register = template.Library()


@register.filter(name='key')
def key(d, key_name):
    if d is not None:
        if key_name in d:
            return d[key_name]

    return ''


@register.filter(name='value')
def value(d, key_name):
    if d is not None:
        if key_name in d:
            return d[key_name]

    return ''


@register.filter(name='minval')
def minval(d, key_name):
    if d is not None:
        if d.get(key_name) is not None:
            minval = d.get(key_name).get('minval')
            if minval is not None:
                return minval

    return ''


@register.filter(name='maxval')
def maxval(d, key_name):
    if d is not None:
        if d.get(key_name) is not None:
            maxval = d.get(key_name).get('maxval')
            if maxval is not None:
                return maxval

    return ''
