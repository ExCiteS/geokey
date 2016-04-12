"""Tests for models of users."""

from django.test import TestCase

from oauth2_provider.models import AccessToken
from geokey.applications.tests.model_factories import ApplicationFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory

from .model_factories import UserGroupFactory, UserFactory
from ..models import UserGroup


class UserTest(TestCase):
    def test_reset_password(self):
        user = UserFactory.create()
        app = ApplicationFactory.create()
        AccessToken.objects.create(
            user=user,
            application=app,
            token='df0af6a395b4cd072445b3832e9379bfee257da0',
            scope=1,
            expires='2030-12-31T23:59:00+00:00'
        )

        user.reset_password('123456')

        self.assertEqual(0, AccessToken.objects.filter(user=user).count())


class UserGroupTest(TestCase):
    def test_update_where_clause(self):
        project = ProjectFactory.create()
        cat_1 = CategoryFactory.create(**{'project': project})
        cat_2 = CategoryFactory.create(**{'project': project})
        usergroup = UserGroupFactory.create(**{'project': project})
        usergroup.filters = {
            cat_1.id: {},
            cat_2.id: {}
        }
        usergroup.save()

        self.assertIn(
            UserGroup.objects.get(pk=usergroup.id).where_clause,
            [
                '((category_id = %s)) OR ((category_id = %s))' % (
                    cat_2.id, cat_1.id
                ),
                '((category_id = %s)) OR ((category_id = %s))' % (
                    cat_1.id, cat_2.id
                )
            ]
        )

        usergroup.filters = {}
        usergroup.save()

        self.assertEqual(
            UserGroup.objects.get(pk=usergroup.id).where_clause,
            'FALSE'
        )

    def test_contribute_and_moderate(self):
        usergroup = UserGroupFactory.create()

        usergroup.can_moderate = True
        usergroup.save()

        ref_group = UserGroup.objects.get(pk=usergroup.id)
        self.assertTrue(ref_group.can_contribute)
        self.assertTrue(ref_group.can_moderate)

    def test_not_contribute_and_moderate(self):
        usergroup = UserGroupFactory.create()

        usergroup.can_contribute = False
        usergroup.can_moderate = True
        usergroup.save()

        ref_group = UserGroup.objects.get(pk=usergroup.id)
        self.assertTrue(ref_group.can_contribute)
        self.assertTrue(ref_group.can_moderate)

    def test_contribute_and_not_moderate(self):
        usergroup = UserGroupFactory.create()

        usergroup.can_contribute = True
        usergroup.can_moderate = False
        usergroup.save()

        ref_group = UserGroup.objects.get(pk=usergroup.id)
        self.assertTrue(ref_group.can_contribute)
        self.assertFalse(ref_group.can_moderate)

    def test_not_contribute_and_not_moderate(self):
        usergroup = UserGroupFactory.create()

        usergroup.can_contribute = False
        usergroup.can_moderate = False
        usergroup.save()

        ref_group = UserGroup.objects.get(pk=usergroup.id)
        self.assertFalse(ref_group.can_contribute)
        self.assertFalse(ref_group.can_moderate)
