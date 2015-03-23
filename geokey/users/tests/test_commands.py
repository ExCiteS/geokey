from pytz import utc
from datetime import datetime, timedelta

from django.test import TestCase
from django.core import mail

from geokey.projects.tests.model_factories import ProjectF, AdminsFactory
from geokey.contributions.tests.model_factories import ObservationFactory

from ..management.commands.daily_digest import Command
from ..tests.model_factories import UserF


class CommandTest(TestCase):
    def test_get_update_projects(self):
        # Setup everything
        updated_project_1 = ProjectF.create()
        updated_project_2 = ProjectF.create()
        not_updated_project = ProjectF.create()

        for x in range(0, 2):
            for project in [
                    updated_project_1, updated_project_2, not_updated_project]:
                ObservationFactory.create(project=project)

        updated = ObservationFactory.create(project=updated_project_2)

        yesterday = datetime.utcnow().replace(tzinfo=utc)

        ObservationFactory.create(project=updated_project_1)
        updated.update(properties={'key': 'value'}, updator=UserF.create())

        # the tests
        command = Command()
        updated_projects = command.get_updated_projects(yesterday)
        self.assertIn(updated_project_1, updated_projects)
        self.assertIn(updated_project_2, updated_projects)
        self.assertNotIn(not_updated_project, updated_projects)

    def test_get_update_stats(self):
        moderator = UserF.create()
        contributor = UserF.create()
        some_dude = UserF.create()

        project = ProjectF.create(
            add_admins=[moderator],
            add_contributors=[contributor]
        )

        suspended = ObservationFactory.create(
            created_at=(datetime.utcnow() - timedelta(2)).replace(tzinfo=utc),
            project=project,
            creator=contributor,
            status='active'
        )

        updated = ObservationFactory.create(
            project=project,
            creator=contributor
        )

        approved = ObservationFactory.create(
            project=project,
            creator=contributor,
            status='pending'
        )

        yesterday = datetime.utcnow().replace(tzinfo=utc)

        suspended.update(
            properties=None,
            status='pending',
            updator=UserF.create()
        )
        updated.update(properties={'key': 'value'}, updator=UserF.create())
        approved.update(properties=None, status='active', updator=moderator)

        for user in [moderator, contributor]:
            ObservationFactory.create(
                project=project,
                creator=user,
                status='pending'
            )

        command = Command()

        report = command.get_updated_items(project, moderator, yesterday)
        to_moderate = report.get('to_moderate')
        self.assertEqual(len(to_moderate.get('new')), 2)
        self.assertEqual(len(to_moderate.get('suspended')), 1)
        self.assertIsNone(report.get('yours'))

        report = command.get_updated_items(project, contributor, yesterday)

        yours = report.get('yours')
        self.assertEqual(len(yours.get('changed')), 3)
        self.assertEqual(len(yours.get('approved')), 1)
        self.assertEqual(len(yours.get('suspended')), 1)

        report = command.get_updated_items(project, some_dude, yesterday)
        self.assertEqual(report, None)

    def test_daily_digest(self):
        do_not_notify = UserF.create()
        moderator = UserF.create()
        contributor = UserF.create()
        UserF.create()

        project = ProjectF.create(
            add_admins=[moderator],
            add_contributors=[contributor]
        )
        AdminsFactory.create(**{
            'project': project,
            'user': do_not_notify,
            'contact': False
        })

        suspended = ObservationFactory.create(
            created_at=(datetime.utcnow() - timedelta(2)).replace(tzinfo=utc),
            project=project,
            creator=contributor,
            status='active'
        )

        updated = ObservationFactory.create(
            project=project,
            creator=contributor
        )

        approved = ObservationFactory.create(
            project=project,
            creator=contributor,
            status='pending'
        )

        yesterday = datetime.utcnow().replace(tzinfo=utc)

        suspended.update(
            properties=None,
            status='pending',
            updator=UserF.create()
        )
        updated.update(properties={'key': 'value'}, updator=UserF.create())
        approved.update(properties=None, status='active', updator=moderator)

        for user in [moderator, contributor]:
            ObservationFactory.create(
                project=project,
                creator=user,
                status='pending'
            )

        command = Command()
        command.send_daily_digest(yesterday)
        self.assertEquals(len(mail.outbox), 3)
