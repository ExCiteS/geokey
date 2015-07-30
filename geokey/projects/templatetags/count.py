from django import template

register = template.Library()


@register.simple_tag
def minus(count, to_sub):
    return count - to_sub
