from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from .model_factories import UserF, UserGroupF, ProjectF
from ..models import Project, UserGroup


class ProjectTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.public_project = ProjectF.create(**{
            'isprivate': False,
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.private_project = ProjectF.create(**{
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.inactive_project = ProjectF.create(**{
            'status': 'inactive',
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.deleted_project = ProjectF.create(**{
            'status': 'deleted',
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })

    def test_create_project(self):
        creator = UserF.create()

        project = Project.create(
            'Test', 'Test desc', True, creator
        )
        self.assertIsInstance(project.admins, UserGroup)
        self.assertIsInstance(project.contributors, UserGroup)
        self.assertIn(creator, project.admins.users.all())

    @raises(Project.DoesNotExist)
    def test_delete_project(self):
        project = ProjectF.create()
        project.delete()
        Project.objects.get(self.admin, pk=project.id)

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

    def test_get_projects_with_admin(self):
        projects = Project.objects.all(self.admin)
        self.assertEqual(projects.count(), 3)
        self.assertNotIn(self.deleted_project, projects)

    def test_get_projects_with_contributor(self):
        projects = Project.objects.all(self.contributor)
        self.assertEqual(projects.count(), 2)
        self.assertNotIn(self.inactive_project, projects)
        self.assertNotIn(self.deleted_project, projects)

    def test_get_projects_with_non_member(self):
        projects = Project.objects.all(self.non_member)
        self.assertEqual(projects.count(), 1)
        self.assertNotIn(self.private_project, projects)
        self.assertNotIn(self.inactive_project, projects)
        self.assertNotIn(self.deleted_project, projects)

    @raises(Project.DoesNotExist)
    def test_get_deleted_project_with_admin(self):
        Project.objects.get(self.admin, self.deleted_project.id)

    def test_get_private_project_with_admin(self):
        project = Project.objects.get(self.admin, self.private_project.id)
        self.assertEqual(project, self.private_project)

    def test_get_inactive_project_with_admin(self):
        project = Project.objects.get(self.admin, self.inactive_project.id)
        self.assertEqual(project, self.inactive_project)

    def test_get_public_project_with_admin(self):
        project = Project.objects.get(self.admin, self.public_project.id)
        self.assertEqual(project, self.public_project)

    @raises(Project.DoesNotExist)
    def test_get_deleted_project_with_contributor(self):
        Project.objects.get(self.contributor, self.deleted_project.id)

    def test_get_private_project_with_contributor(self):
        project = Project.objects.get(
            self.contributor,
            self.private_project.id
        )
        self.assertEqual(project, self.private_project)

    @raises(PermissionDenied)
    def test_get_inactive_project_with_contributor(self):
        Project.objects.get(self.contributor, self.inactive_project.id)

    def test_get_public_project_with_contributor(self):
        project = Project.objects.get(self.contributor, self.public_project.id)
        self.assertEqual(project, self.public_project)

    @raises(Project.DoesNotExist)
    def test_get_deleted_project_with_non_member(self):
        Project.objects.get(self.non_member, self.deleted_project.id)

    @raises(PermissionDenied)
    def test_get_private_project_with_non_member(self):
        Project.objects.get(self.non_member, self.private_project.id)

    @raises(PermissionDenied)
    def test_get_inactive_project_with_non_member(self):
        Project.objects.get(self.non_member, self.inactive_project.id)

    def test_get_public_project_with_non_member(self):
        project = Project.objects.get(self.non_member, self.public_project.id)
        self.assertEqual(project, self.public_project)

    @raises(Project.DoesNotExist)
    def test_get_deleted_project_as_admin_with_admin(self):
        Project.objects.as_admin(self.admin, self.deleted_project.id)

    def test_get_private_project_as_admin_with_admin(self):
        project = Project.objects.as_admin(self.admin, self.private_project.id)
        self.assertEqual(project, self.private_project)

    def test_get_inactive_project_as_admin_with_admin(self):
        project = Project.objects.as_admin(
            self.admin,
            self.inactive_project.id
        )
        self.assertEqual(project, self.inactive_project)

    def test_get_public_project_as_admin_with_admin(self):
        project = Project.objects.as_admin(self.admin, self.public_project.id)
        self.assertEqual(project, self.public_project)

    @raises(Project.DoesNotExist)
    def test_get_deleted_project_as_admin_with_contributor(self):
        Project.objects.as_admin(self.contributor, self.deleted_project.id)

    @raises(PermissionDenied)
    def test_get_private_project_as_admin_with_contributor(self):
        project = Project.objects.as_admin(
            self.contributor,
            self.private_project.id
        )
        self.assertEqual(project, self.private_project)

    @raises(PermissionDenied)
    def test_get_inactive_project_as_admin_with_contributor(self):
        Project.objects.as_admin(self.contributor, self.inactive_project.id)

    @raises(PermissionDenied)
    def test_get_public_project_as_admin_with_contributor(self):
        project = Project.objects.as_admin(
            self.contributor,
            self.public_project.id
        )
        self.assertEqual(project, self.public_project)

    @raises(Project.DoesNotExist)
    def test_get_deleted_project_as_admin_with_non_member(self):
        Project.objects.as_admin(self.non_member, self.deleted_project.id)

    @raises(PermissionDenied)
    def test_get_private_project_as_admin_with_non_member(self):
        Project.objects.as_admin(self.non_member, self.private_project.id)

    @raises(PermissionDenied)
    def test_get_inactive_project_as_admin_with_non_member(self):
        Project.objects.as_admin(self.non_member, self.inactive_project.id)

    @raises(PermissionDenied)
    def test_get_public_project_as_admin_with_non_member(self):
        project = Project.objects.as_admin(
            self.non_member,
            self.public_project.id
        )
        self.assertEqual(project, self.public_project)
