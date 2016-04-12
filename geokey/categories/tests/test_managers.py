"""Tests for managers of categories."""

from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from geokey.projects.tests.model_factories import UserFactory, ProjectFactory
from geokey.projects.models import Project

from ..models import Field, Category, LookupValue, MultipleLookupValue

from .model_factories import (
    TextFieldFactory,
    CategoryFactory,
    LookupValueFactory,
    MultipleLookupValueFactory
)


class CategoryManagerTest(TestCase):
    def test_access_with_projct_admin(self):
        admin = UserFactory.create()

        project = ProjectFactory.create(
            add_admins=[admin],
            **{'isprivate': True}
        )

        CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        CategoryFactory(**{
            'project': project,
            'status': 'inactive'
        })

        self.assertEqual(
            len(Category.objects.get_list(admin, project.id)), 2
        )

    def test_access_with_projct_contributor(self):
        contributor = UserFactory.create()

        project = ProjectFactory.create(
            add_contributors=[contributor],
            **{'isprivate': True}
        )

        active = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        CategoryFactory(**{
            'project': project,
            'status': 'inactive'
        })

        types = Category.objects.get_list(contributor, project.id)
        self.assertEqual(len(types), 1)
        self.assertIn(active, types)

    @raises(Project.DoesNotExist)
    def test_access_with_projct_non_member(self):
        contributor = UserFactory.create()

        project = ProjectFactory.create()

        CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        CategoryFactory(**{
            'project': project,
            'status': 'inactive'
        })
        Category.objects.get_list(contributor, project.id)

    def test_access_active_with_admin(self):
        admin = UserFactory.create()

        project = ProjectFactory.create(
            add_admins=[admin],
            **{'isprivate': True}
        )

        active_type = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, Category.objects.get_single(
            admin, project.id, active_type.id))

    def test_access_inactive_with_admin(self):
        admin = UserFactory.create()
        project = ProjectFactory.create(
            add_admins=[admin],
            **{'isprivate': True}
        )
        inactive_type = CategoryFactory(**{
            'project': project,
            'status': 'inactive'
        })
        self.assertEqual(inactive_type, Category.objects.get_single(
            admin, project.id, inactive_type.id))

    def test_access_active_with_contributor(self):
        contributor = UserFactory.create()

        project = ProjectFactory.create(
            add_contributors=[contributor],
            **{'isprivate': True}
        )

        active_type = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, Category.objects.get_single(
            contributor, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_access_inactive_with_contributor(self):
        contributor = UserFactory.create()

        project = ProjectFactory.create(
            add_contributors=[contributor],
            **{'isprivate': True}
        )
        inactive_type = CategoryFactory(**{
            'project': project,
            'status': 'inactive'
        })
        Category.objects.get_single(
            contributor, project.id, inactive_type.id)

    @raises(Project.DoesNotExist)
    def test_access_active_with_non_member(self):
        contributor = UserFactory.create()

        project = ProjectFactory.create(**{
            'isprivate': True,
        })

        active_type = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, Category.objects.get_single(
            contributor, project.id, active_type.id))

    @raises(Project.DoesNotExist)
    def test_access_inactive_with_non_member(self):
        contributor = UserFactory.create()

        project = ProjectFactory.create(**{
            'isprivate': True,
        })
        inactive_type = CategoryFactory(**{
            'project': project,
            'status': 'inactive'
        })
        Category.objects.get_single(
            contributor, project.id, inactive_type.id)

    def test_admin_access_with_admin(self):
        admin = UserFactory.create()

        project = ProjectFactory.create(
            add_admins=[admin],
            **{'isprivate': True}
        )

        active_type = CategoryFactory(**{
            'project': project
        })

        self.assertEqual(active_type, Category.objects.as_admin(
            admin, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_admin_access_with_contributor(self):
        user = UserFactory.create()

        project = ProjectFactory.create(
            add_contributors=[user],
            **{'isprivate': True}
        )

        active_type = CategoryFactory(**{
            'project': project
        })

        Category.objects.as_admin(user, project.id, active_type.id)

    @raises(Project.DoesNotExist)
    def test_admin_access_with_non_member(self):
        user = UserFactory.create()

        project = ProjectFactory.create(**{
            'isprivate': True
        })

        active_type = CategoryFactory(**{
            'project': project
        })

        Category.objects.as_admin(user, project.id, active_type.id)


class FieldManagerTest(TestCase):
    def test_access_fields_with_admin(self):
        admin = UserFactory.create()
        project = ProjectFactory.create(
            add_admins=[admin],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        TextFieldFactory.create(**{
            'status': 'inactive',
            'category': category
        })
        self.assertEqual(
            len(Field.objects.get_list(admin, project.id, category.id)),
            2
        )

    def test_access_active_field_with_admin(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            add_admins=[user],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, category.id, field.id))

    def test_access_inactive_field_with_admin(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            add_admins=[user],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'category': category
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, category.id, field.id))

    def test_admin_access_active_field_with_admin(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            add_admins=[user],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        self.assertEqual(
            field, Field.objects.as_admin(
                user, project.id, category.id, field.id))

    def test_access_fields_with_contributor(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        inactive = TextFieldFactory.create(**{
            'status': 'inactive',
            'category': category
        })
        fields = Field.objects.get_list(user, project.id, category.id)
        self.assertEqual(len(fields), 1)
        self.assertNotIn(inactive, fields)

    def test_access_active_field_with_contributor(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, category.id, field.id))

    @raises(PermissionDenied)
    def test_access_active_field_inactive_cat_with_contributor(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'inactive'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        Field.objects.get_single(user, project.id, category.id, field.id)

    @raises(PermissionDenied)
    def test_access_inactive_field_with_contributor(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'category': category
        })
        Field.objects.get_single(
            user, project.id, category.id, field.id)

    @raises(PermissionDenied)
    def test_admin_access_active_field_with_contributor(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            add_contributors=[user],
            **{'isprivate': True}
        )
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        Field.objects.as_admin(
            user, project.id, category.id, field.id)

    @raises(Project.DoesNotExist)
    def test_access_fields_with_non_member(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'isprivate': True})
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        TextFieldFactory.create(**{
            'status': 'inactive',
            'category': category
        })
        Field.objects.get_list(user, project.id, category.id)

    @raises(Project.DoesNotExist)
    def test_access_active_field_with_non_member(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'isprivate': True})
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        Field.objects.get_single(
            user, project.id, category.id, field.id)

    @raises(Project.DoesNotExist)
    def test_access_inactive_field_with_non_member(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'isprivate': True})
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'category': category
        })
        Field.objects.get_single(
            user, project.id, category.id, field.id)

    @raises(Project.DoesNotExist)
    def test_admin_access_active_field_with_non_member(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'isprivate': True})
        category = CategoryFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'category': category
        })
        Field.objects.as_admin(
            user, project.id, category.id, field.id)


class LookupManagerTest(TestCase):
    def tearDown(self):
        for lookup_value in LookupValue.objects.all():
            if lookup_value.symbol is not None:
                lookup_value.symbol.delete()

        for lookup_value in MultipleLookupValue.objects.all():
            if lookup_value.symbol is not None:
                lookup_value.symbol.delete()

    def test_with_lookup_value(self):
        LookupValueFactory.create_batch(5, **{'status': 'active'})
        LookupValueFactory.create_batch(5, **{'status': 'deleted'})

        values = LookupValue.objects.active()
        self.assertEqual(len(values), 5)

    def test_with_multiple_lookup_value(self):
        MultipleLookupValueFactory.create_batch(5, **{'status': 'active'})
        MultipleLookupValueFactory.create_batch(5, **{'status': 'deleted'})

        values = MultipleLookupValue.objects.active()
        self.assertEqual(len(values), 5)
