import moment

from django import template

register = template.Library()


def get_user_name(user):
    if user.first_name and user.last_name:
        return user.get_full_name()
    else:
        return user.username


def format_date(date):
    return moment.date(date).format('D/M/YYYY at h:m A')


@register.simple_tag
def meta(observation):
    username = get_user_name(observation.creator)
    date = format_date(observation.created_at)

    if observation.version == 1:
        return 'Created by %s on %s.' % (username, date)
    else:
        version_1 = observation.data.get(version=1)
        creator = get_user_name(version_1.creator)
        create_date = format_date(version_1.created_at)
        return 'Created by %s on %s. Updated to version %s by %s on %s.' % (
            creator, create_date, observation.version,
            username, date)
