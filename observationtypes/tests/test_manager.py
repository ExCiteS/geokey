from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF
from projects.models import Project

from ..models import Field, ObservationType

from .model_factories import (
    TextFieldFactory, ObservationTypeFactory
)


class ObservationTypeManagerTest(TestCase):
    def test_create(self):
        project = ProjectF.create()
        category = ObservationType.objects.create(
            name='Test',
            project=project,
            creator=project.creator,
        )

        views = project.views.all()
        self.assertEqual(len(views), 1)
        self.assertEqual(views[0].name, category.name)

    def test_access_with_projct_admin(self):
        admin = UserF.create()

        project = ProjectF.create(
            add_admins=[admin],
            **{'isprivate': True}
        )

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

        project = ProjectF.create(
            add_contributors=[contributor],
            **{'isprivate': True}
        )

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

    @raises(Project.DoesNotExist)
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

        project = ProjectF.create(
            add_admins=[admin],
            **{'isprivate': True}
        )

        active_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, ObservationType.objects.get_single(
            admin, project.id, active_type.id))

    def test_access_inactive_with_admin(self):
        admin = UserF.create()
        project = ProjectF.create(
            add_admins=[admin],
            **{'isprivate': True}
        )
        inactive_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        self.assertEqual(inactive_type, ObservationType.objects.get_single(
            admin, project.id, inactive_type.id))

    def test_access_active_with_contributor(self):
        contributor = UserF.create()

        project = ProjectF.create(
            add_contributors=[contributor],
            **{'isprivate': True}
        )

        active_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, ObservationType.objects.get_single(
            contributor, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_access_inactive_with_contributor(self):
        contributor = UserF.create()

        project = ProjectF.create(
            add_contributors=[contributor],
            **{'isprivate': True}
        )
        inactive_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        ObservationType.objects.get_single(
            contributor, project.id, inactive_type.id)

    @raises(Project.DoesNotExist)
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

    @raises(Project.DoesNotExist)
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

        project = ProjectF.create(
            add_admins=[admin],
            **{'isprivate': True}
        )

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        self.assertEqual(active_type, ObservationType.objects.as_admin(
            admin, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_admin_access_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(
            add_contributors=[user],
            **{'isprivate': True}
        )

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        ObservationType.objects.as_admin(user, project.id, active_type.id)

    @raises(Project.DoesNotExist)
    def test_admin_access_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True
        })

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        ObservationType.objects.as_admin(user, project.id, active_type.id)


class FieldManagerTest(TestCase):
    def test_access_fields_with_admin(self):
        admin = UserF.create()
        project = ProjectF.create(
            add_admins=[admin],
            **{'isprivate': True}
        )
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        self.assertEqual(
            len(Field.objects.get_list(
                admin, project.id, observation_type.id)),
            2
        )

    def test_access_active_field_with_admin(self):
        user = UserF.create()
        project = ProjectF.create(
            add_admins=[user],
            **{'isprivate': True}
        )
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, observation_type.id, field.id))

    def test_access_inactive_field_with_admin(self):
        user = UserF.create()
        project = ProjectF.create(
            add_admins=[user],
            **{'isprivate': True}
        )
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, observation_type.id, field.id))

    def test_admin_access_active_field_with_admin(self):
        user = UserF.create()
        project = ProjectF.create(
            add_admins=[user],
            **{'isprivate': True}
        )
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        self.assertEqual(
            field, Field.objects.as_admin(
                user, project.id, observation_type.id, field.id))

    def test_access_fields_with_contributor(self):
        user = UserF.create()
        project = ProjectF.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        inactive = TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        fields = Field.objects.get_list(user, project.id, observation_type.id)
        self.assertEqual(len(fields), 1)
        self.assertNotIn(inactive, fields)

    def test_access_active_field_with_contributor(self):
        user = UserF.create()
        project = ProjectF.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, observation_type.id, field.id))

    @raises(PermissionDenied)
    def test_access_inactive_field_with_contributor(self):
        user = UserF.create()
        project = ProjectF.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        Field.objects.get_single(
            user, project.id, observation_type.id, field.id)

    @raises(PermissionDenied)
    def test_admin_access_active_field_with_contributor(self):
        user = UserF.create()
        project = ProjectF.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        Field.objects.as_admin(
            user, project.id, observation_type.id, field.id)

    @raises(Project.DoesNotExist)
    def test_access_fields_with_non_member(self):
        user = UserF.create()
        project = ProjectF.create(**{'isprivate': True})
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        Field.objects.get_list(user, project.id, observation_type.id)

    @raises(Project.DoesNotExist)
    def test_access_active_field_with_non_member(self):
        user = UserF.create()
        project = ProjectF.create(**{'isprivate': True})
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        Field.objects.get_single(
            user, project.id, observation_type.id, field.id)

    @raises(Project.DoesNotExist)
    def test_access_inactive_field_with_non_member(self):
        user = UserF.create()
        project = ProjectF.create(**{'isprivate': True})
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        Field.objects.get_single(
            user, project.id, observation_type.id, field.id)

    @raises(Project.DoesNotExist)
    def test_admin_access_active_field_with_non_member(self):
        user = UserF.create()
        project = ProjectF.create(**{'isprivate': True})
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        Field.objects.as_admin(
            user, project.id, observation_type.id, field.id)
