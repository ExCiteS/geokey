from django.test import TestCase

from .model_factories import UserGroupF
from ..models import UserGroup


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
