#!/usr/bin/python

import sys
import os

from django.conf import settings
from django.contrib.sites.models import Site

from datetime import datetime, timedelta
from pytz import utc

from django.core.management.base import NoArgsCommand
from django.db.models import Q
from django.core import mail

from django.template.loader import get_template
from django.template import Context

from geokey.projects.models import Project, Admins
from geokey.users.models import User
from geokey.contributions.models import Observation


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

        try:
            notify = Admins.objects.get(user=user, project=project).contact
        except Admins.DoesNotExist:
            notify = True

        if notify:
            new_items = project.observations.filter(
                created_at__gte=yesterday, status='pending')
            updated_items = project.observations.filter(
                updated_at__gte=yesterday,
                created_at__lt=yesterday
            )

            if updated_items.count() > 0 or new_items.count() > 0:

                if project.can_moderate(user):
                    items['to_moderate'] = {
                        'new': new_items,
                        'reported': updated_items.filter(status='review'),
                        'suspended': updated_items.filter(status='pending')
                    }
                if project.can_contribute(user):
                    approved = []
                    reported = []
                    suspended = []

                    for item in updated_items.filter(creator=user):
                        try:
                            historical = item.history.as_of(yesterday)

                            if (item.status == 'pending' and
                                    historical.status == 'active'):
                                suspended.append(item)
                            elif (item.status == 'review' and
                                    historical.status == 'active'):
                                reported.append(item)
                            elif (item.status == 'active' and
                                    historical.status == 'pending'):
                                approved.append(item)
                        except Observation.DoesNotExist:
                            pass

                        items['yours'] = {
                            'changed': updated_items.filter(creator=user),
                            'approved': approved,
                            'reported': reported,
                            'suspended': suspended
                        }
                    return items

        return None

    def send_daily_digest(self, yesterday):
        """
        Creates a daily digest for all users registered in the system and sends
        the digest to theses users. Digests will only be sent if there are
        relevant updates in at least one project.
        """
        messages = []

        updated_projects = self.get_updated_projects(yesterday)
        platform = Site.objects.get(pk=settings.SITE_ID).name

        for user in User.objects.exclude(display_name='AnonymousUser'):
            reports = []
            for project in updated_projects:
                updated_items = self.get_updated_items(
                    project,
                    user,
                    yesterday
                )

                if updated_items is not None:
                    to_moderate = updated_items.pop('to_moderate', None)
                    yours = updated_items.pop('yours', None)

                    if to_moderate is not None or yours is not None:
                        reports.append({
                            'project': project.name,
                            'to_moderate': to_moderate,
                            'yours': yours
                        })

            if len(reports) > 0:
                email_text = get_template('users/daily_digest.txt')
                context = Context({
                    'user': user.display_name,
                    'yesterday': yesterday.strftime('%d %B %Y'),
                    'reports': reports,
                    'platform': platform
                })
                text = email_text.render(context)

                email = mail.EmailMessage(
                    '%s daily digest for %s' % (
                        platform,
                        yesterday.strftime('%d %B %Y')
                    ),
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

    def handle(self, *args, **options):
        now = datetime.utcnow() - timedelta(1)
        yesterday = datetime(
            now.year, now.month, now.day, 0, 0, 0).replace(tzinfo=utc)

        self.send_daily_digest(yesterday)
