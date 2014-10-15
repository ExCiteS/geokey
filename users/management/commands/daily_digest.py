from datetime import datetime, timedelta
from pytz import utc

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.db import connection
from django.db.models import Q
from django.core import mail


from projects.models import Project
from users.models import User
from contributions.models import Observation

class Command(NoArgsCommand):
    def get_updated_projects(self, yesterday):
        """
        Returns all projects that where updated during the previous day
        """
        projects = Project.objects.filter(status='active')
        return projects.filter(
            Q(observations__created_at__gte=yesterday) |
            Q(observations__updated_at__gte=yesterday)).distinct()

    def get_updated_items(self, project, user, yesterday):
        """
        Returns all updated contributions of a project for the given users.

        Returns a dict if the user is moderator or contributor, `to_moderate`
        is only available when the user is a moderator:
        {
            'to_moderate': {
                'new': [],
                'reported': []
            },
            'yours': {
                'changed': []
                'approved': []
                'reports': []
            }
        }

        Returns `None` if the user is neither moderator or contributor of the
        project.
        """
        items = {}

        new_items = project.observations.filter(
            created_at__gte=yesterday, status='pending')
        updated_items = project.observations.filter(updated_at__gte=yesterday)

        if updated_items.count() > 0 and new_items > 0:

            if project.can_moderate(user):
                items['to_moderate'] = {
                    'new': new_items,
                    'reported': updated_items.filter(status='pending')
                }
            if project.can_contribute(user):
                approved = []
                reported = []

                for item in updated_items.filter(creator=user):
                    try:
                        historical = item.history.as_of(yesterday)

                        if (item.status == 'pending' and
                                historical.status == 'active'):
                            reported.append(item)
                        if (item.status == 'active' and
                                historical.status == 'pending'):
                            approved.append(item)
                    except Observation.DoesNotExist:
                        pass

                items['yours'] = {
                     'changed': updated_items.filter(creator=user),
                     'approved': approved,
                     'reported': reported
                }
                return items

        return None

    def daily_digest(self):
        """
        Creates a daily digest for all users registered in the system and sends
        the digest to theses users. Digests will only be sent if there are
        relevant updates in at least one project.
        """
        messages = []
        now = datetime.utcnow() - timedelta(1)
        yesterday = datetime(
            now.year, now.month, now.day, 0, 0, 0).replace(tzinfo=utc)

        updated_projects = self.get_updated_projects(yesterday)

        for user in User.objects.all():
            reports = []
            for project in updated_projects:
                updated_items = self.get_updated_items(project, user, yesterday)

                if updated_items is not None:
                    project_report = ''

                    to_moderate = updated_items.pop('to_moderate', None)
                    if to_moderate is not None:
                        text = ('  Please moderate %s new contributions and %s '
                                'reported contributions.' % (
                                    len(to_moderate.get('new')),
                                    len(to_moderate.get('reported'))
                                ))
                        project_report = project_report + text + '\n'

                    yours = updated_items.pop('yours', None)
                    if yours is not None:
                        text = ('  %s of your contributions have been changed.'
                                ' %s where approved, %s where reported.' % (
                                len(yours.get('changed')),
                                len(yours.get('approved')),
                                len(yours.get('reported'))
                            ))
                        project_report = project_report + text + '\n\n\n'

                    if len(project_report) > 0:
                        reports.append(
                            '- %s\n\n%s' % (project.name, project_report))

            if len(reports) > 0:
                text = ('Dear %s,\n\nhere\'s an overview of what happened in '
                    'your projects on %s:\n\n %sHappy mapping, the GeoKey Team.' %
                    (
                        user.display_name,
                        yesterday.strftime('%d %B %Y'),
                        '\n\n\n'.join(reports)
                    ))

                email = mail.EmailMessage(
                    'GeoKey daily digest for ' + yesterday.strftime('%d %B %Y'),
                    text,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                messages.append(email)

        if len(messages) > 0:
            connection = mail.get_connection()
            connection.open()
            connection.send_messages(messages)
            connection.close()

