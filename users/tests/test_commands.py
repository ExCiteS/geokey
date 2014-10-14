from pytz import utc
from datetime import datetime, timedelta

from django.test import TestCase
from django.core import mail

from projects.tests.model_factories import ProjectF
from projects.models  import Project
from contributions.tests.model_factories import ObservationFactory

from..models import User
from ..management.commands.daily_digest import Command
from ..tests.model_factories import UserF

class CommandTest(TestCase):
    def test_get_update_projects(self):
        # Setup everything
        updated_project_1 = ProjectF.create()
        updated_project_2 = ProjectF.create()
        not_updated_project = ProjectF.create()

        for x in range(0, 2):
            for project in [updated_project_1, updated_project_2, not_updated_project]:
                o = ObservationFactory.create(project=project)

        updated = ObservationFactory.create(project=updated_project_2)

        yesterday = datetime.utcnow().replace(tzinfo=utc)

        created = ObservationFactory.create(project=updated_project_1)
        updated.update(attributes={'key': 'value'}, updator=UserF.create())

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

        reported = ObservationFactory.create(
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
        
        reported.update(attributes=None, status='pending', updator=UserF.create())
        updated.update(attributes={'key': 'value'}, updator=UserF.create())
        approved.update(attributes=None, status='active', updator=moderator)

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
        self.assertEqual(len(to_moderate.get('reported')), 1)

        yours = report.get('yours')
        self.assertEqual(len(yours.get('changed')), 0)
        self.assertEqual(len(yours.get('approved')), 0)
        self.assertEqual(len(yours.get('reported')), 0)

        report = command.get_updated_items(project, contributor, yesterday)

        yours = report.get('yours')
        self.assertEqual(len(yours.get('changed')), 3)
        self.assertEqual(len(yours.get('approved')), 1)
        self.assertEqual(len(yours.get('reported')), 1)

        report = command.get_updated_items(project, some_dude, yesterday)
        self.assertEqual(report, None)

    def test_daily_digest(self):
        moderator = UserF.create()
        contributor = UserF.create()
        some_dude = UserF.create()

        project = ProjectF.create(
            add_admins=[moderator],
            add_contributors=[contributor]
        )

        reported = ObservationFactory.create(
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
        
        reported.update(attributes=None, status='pending', updator=UserF.create())
        updated.update(attributes={'key': 'value'}, updator=UserF.create())
        approved.update(attributes=None, status='active', updator=moderator)

        for user in [moderator, contributor]:
            ObservationFactory.create(
                project=project,
                creator=user,
                status='pending'
            )

        command = Command()
        command.daily_digest()
        self.assertEquals(len(mail.outbox), 3)
