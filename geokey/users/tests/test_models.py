from django.test import TestCase

from oauth2_provider.models import AccessToken
from geokey.applications.tests.model_factories import ApplicationFactory

from .model_factories import UserGroupF, UserF
from ..models import UserGroup


class UserTest(TestCase):
    def test_reset_password(self):
        user = UserF.create()
        app = ApplicationFactory.create()
        AccessToken.objects.create(
            user=user,
            application=app,
            token='df0af6a395b4cd072445b3832e9379bfee257da0',
            scope=1,
            expires='2030-12-31 23:59'
        )

        user.reset_password('123456')

        self.assertEqual(0, AccessToken.objects.filter(user=user).count())


class UserGroupPreSaveSignalTest(TestCase):
    def test_contribute_and_moderate(self):
        usergroup = UserGroupF.create()

        usergroup.can_moderate = True
        usergroup.save()

        ref_group = UserGroup.objects.get(pk=usergroup.id)
        self.assertTrue(ref_group.can_contribute)
        self.assertTrue(ref_group.can_moderate)

    def test_not_contribute_and_moderate(self):
        usergroup = UserGroupF.create()

        usergroup.can_contribute = False
        usergroup.can_moderate = True
        usergroup.save()

        ref_group = UserGroup.objects.get(pk=usergroup.id)
        self.assertTrue(ref_group.can_contribute)
        self.assertTrue(ref_group.can_moderate)

    def test_contribute_and_not_moderate(self):
        usergroup = UserGroupF.create()

        usergroup.can_contribute = True
        usergroup.can_moderate = False
        usergroup.save()

        ref_group = UserGroup.objects.get(pk=usergroup.id)
        self.assertTrue(ref_group.can_contribute)
        self.assertFalse(ref_group.can_moderate)

    def test_not_contribute_and_not_moderate(self):
        usergroup = UserGroupF.create()

        usergroup.can_contribute = False
        usergroup.can_moderate = False
        usergroup.save()

        ref_group = UserGroup.objects.get(pk=usergroup.id)
        self.assertFalse(ref_group.can_contribute)
        self.assertFalse(ref_group.can_moderate)
