from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import UserF

from .model_factories import ApplicationFactory

from ..models import Application


class ApplicationModelTest(TestCase):
    def setUp(self):
        self.user1 = UserF()
        self.user2 = UserF()
        self.app1 = ApplicationFactory(**{
            'creator': self.user1
        })
        self.app2 = ApplicationFactory(**{
            'creator': self.user1
        })
        self.app3 = ApplicationFactory(**{
            'creator': self.user2
        })
        self.deleted_app = ApplicationFactory(**{
            'creator': self.user1,
            'status': 'deleted'
        })

    @raises(Application.DoesNotExist)
    def test_delete_app(self):
        app = ApplicationFactory()
        app.delete()
        Application.objects.get(pk=app.id)

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
        app = Application.objects.get_single(self.user1, self.app1.id)
        self.assertEqual(app, self.app1)

    @raises(PermissionDenied)
    def test_get_single_app_with_user2(self):
        Application.objects.get_single(self.user2, self.app1.id)
