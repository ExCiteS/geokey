import moment

from django import template

register = template.Library()


def format_date(date):
    return moment.date(date).format('D/M/YYYY at h:m A')


@register.simple_tag
def meta(observation):
    date = format_date(observation.created_at)

    if observation.version == 1:
        return 'Created by %s on %s.' % (
            observation.creator.display_name, date)
    else:
        return 'Created by %s on %s. Updated to version %s by %s on %s.' % (
            observation.creator.display_name(), date, observation.version,
            observation.updator.display_name, date)
