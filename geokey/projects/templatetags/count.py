"""Template tags for counting."""

from django import template

register = template.Library()


@register.simple_tag
def more_link_text(count, singular, plural, minus=5):
    return 'Show {more_count} more {label}'.format(
        more_count=count-minus,
        label=(plural if count-minus != 1 else singular)
    )
