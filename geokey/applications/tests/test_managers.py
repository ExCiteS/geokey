"""Tests for managers of applications."""

from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from geokey.projects.tests.model_factories import UserFactory

from .model_factories import ApplicationFactory

from ..models import Application


class ApplicationManagerTest(TestCase):
    def setUp(self):
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.app1 = ApplicationFactory(**{
            'user': self.user1
        })
        self.app2 = ApplicationFactory(**{
            'user': self.user1
        })
        self.app3 = ApplicationFactory(**{
            'user': self.user2
        })
        self.deleted_app = ApplicationFactory(**{
            'user': self.user1,
            'status': 'deleted'
        })

    def test_get_apps_with_user1(self):
        apps = Application.objects.get_list(self.user1)
        self.assertEqual(len(apps), 2)
        self.assertNotIn(self.deleted_app, apps)
        self.assertNotIn(self.app3, apps)

    def test_get_apps_with_user2(self):
        apps = Application.objects.get_list(self.user2)
        self.assertEqual(len(apps), 1)
        self.assertNotIn(self.deleted_app, apps)
        self.assertNotIn(self.app1, apps)
        self.assertNotIn(self.app2, apps)

    def test_get_single_app_with_user1(self):
        app = Application.objects.as_owner(self.user1, self.app1.id)
        self.assertEqual(app, self.app1)

    @raises(PermissionDenied)
    def test_get_single_app_with_user2(self):
        Application.objects.as_owner(self.user2, self.app1.id)
