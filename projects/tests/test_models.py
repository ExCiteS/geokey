from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from nose.tools import raises

from dataviews.tests.model_factories import ViewFactory

from .model_factories import UserF, ProjectF
from ..models import Project


class ProjectTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_member = UserF.create()

        self.private_project = ProjectF.create(
            add_admins=[self.admin, self.creator],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member]
        )

    def test_create_project(self):
        creator = UserF.create()

        project = Project.create(
            'Test', 'Test desc', True, creator
        )
        self.assertIn(creator, project.admins.all())

    @raises(Project.DoesNotExist)
    def test_delete_project(self):
        project = ProjectF.create()
        project.delete()
        Project.objects.get(pk=project.id)

    def test_str(self):
        project = ProjectF.create(**{
            'name': 'Name',
            'status': 'inactive',
            'isprivate': False
        })
        self.assertEqual(
            str(project),
            'Name status: inactive private: False'
        )

    def test_is_admin(self):
        self.assertTrue(self.private_project.is_admin(self.admin))
        self.assertTrue(self.private_project.is_admin(self.creator))
        self.assertFalse(self.private_project.is_admin(self.contributor))
        self.assertFalse(self.private_project.is_admin(self.non_member))
        self.assertFalse(self.private_project.is_admin(self.view_member))

    def test_can_contribute(self):
        self.assertTrue(self.private_project.can_contribute(self.admin))
        self.assertTrue(self.private_project.can_contribute(self.creator))
        self.assertTrue(self.private_project.can_contribute(self.contributor))
        self.assertFalse(self.private_project.can_contribute(self.non_member))
        self.assertFalse(self.private_project.can_contribute(self.view_member))

    def test_can_access(self):
        self.assertTrue(self.private_project.can_access(self.admin))
        self.assertTrue(self.private_project.can_access(self.creator))
        self.assertTrue(self.private_project.can_access(self.contributor))
        self.assertFalse(self.private_project.can_access(self.non_member))
        self.assertTrue(self.private_project.can_access(self.view_member))


class ProjectIsInvolved(TestCase):
    def test_public_without_public_views(self):
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin, self.creator],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member],
            **{'isprivate': False}
        )

        self.assertTrue(self.project.is_involved(self.admin))
        self.assertTrue(self.project.is_involved(self.creator))
        self.assertTrue(self.project.is_involved(self.contributor))
        self.assertTrue(self.project.is_involved(self.view_member))
        self.assertFalse(self.project.is_involved(self.non_member))
        self.assertFalse(self.project.is_involved(AnonymousUser()))

    def test_public_with_public_views(self):
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin, self.creator],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member],
            **{'isprivate': False}
        )

        ViewFactory(**{'isprivate': False})

        self.assertTrue(self.project.is_involved(self.admin))
        self.assertTrue(self.project.is_involved(self.creator))
        self.assertTrue(self.project.is_involved(self.contributor))
        self.assertTrue(self.project.is_involved(self.view_member))
        self.assertFalse(self.project.is_involved(self.non_member))
        self.assertFalse(self.project.is_involved(AnonymousUser()))
