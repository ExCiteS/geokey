from django import template

register = template.Library()


@register.simple_tag
def is_selected(value, key, d):
    if d is not None:
        if d.get(key) is not None:
            if str(value) in d[key]:
                return 'selected'

    return ''


@register.filter(name='is_in')
def is_in(d, key_name):
    if d is not None:
        if str(key_name) in d:
            return True
            return 'checked="checked"'
    return False
    return ''


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
