from django import template

register = template.Library()


@register.simple_tag
def more_link_text(count, singular, plural, minus=5):
    return 'Show {more_count} more {label}'.format(
        more_count=count-minus,
        label=(plural if count-minus != 1 else singular)
    )


@register.simple_tag
def minus(count, to_sub):
    return count - to_sub


@register.simple_tag
def plus(count, to_add):
    return count + to_add
