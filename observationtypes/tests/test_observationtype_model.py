from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF, UserGroupF

from .model_factories import ObservationTypeFactory

from ..models import ObservationType


class ObservationtypeTest(TestCase):
    #
    # ACCESS
    #
    def test_access_with_projct_admin(self):
        admin = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'creator': admin,
            'admins': UserGroupF(add_users=[admin]),
        })

        ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })

        self.assertEqual(
            len(ObservationType.objects.get_list(admin, project.id)), 2
        )

    def test_access_with_projct_contributor(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[contributor]),
        })

        active = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })

        types = ObservationType.objects.get_list(contributor, project.id)
        self.assertEqual(len(types), 1)
        self.assertIn(active, types)

    @raises(PermissionDenied)
    def test_access_with_projct_non_member(self):
        contributor = UserF.create()

        project = ProjectF.create()

        ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        ObservationType.objects.get_list(contributor, project.id)

    def test_access_active_with_admin(self):
        admin = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[admin]),
        })

        active_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, ObservationType.objects.get_single(
            admin, project.id, active_type.id))

    def test_access_inactive_with_admin(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[admin]),
        })
        inactive_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        self.assertEqual(inactive_type, ObservationType.objects.get_single(
            admin, project.id, inactive_type.id))

    def test_access_active_with_contributor(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[contributor]),
        })

        active_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, ObservationType.objects.get_single(
            contributor, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_access_inactive_with_contributor(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[contributor]),
        })
        inactive_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        ObservationType.objects.get_single(
            contributor, project.id, inactive_type.id)

    @raises(PermissionDenied)
    def test_access_active_with_non_member(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
        })

        active_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, ObservationType.objects.get_single(
            contributor, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_access_inactive_with_non_member(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
        })
        inactive_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        ObservationType.objects.get_single(
            contributor, project.id, inactive_type.id)

    def test_admin_access_with_admin(self):
        admin = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[admin]),
        })

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        self.assertEqual(active_type, ObservationType.objects.as_admin(
            admin, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_admin_access_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[user]),
        })

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        ObservationType.objects.as_admin(user, project.id, active_type.id)

    @raises(PermissionDenied)
    def test_admin_access_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True
        })

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        ObservationType.objects.as_admin(user, project.id, active_type.id)
