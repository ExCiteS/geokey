from django import template

register = template.Library()


@register.simple_tag
def minus(count, to_sub):
    return count - to_sub


@register.simple_tag
def plus(count, to_add):
    return count + to_add
