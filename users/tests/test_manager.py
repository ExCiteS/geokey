from django.test import TestCase
from nose.tools import raises

from ..models import User


class TestCreateSuperUser(TestCase):
    def test(self):
        email = 'bla@example.com'
        display_name = 'superuser'
        password = 'password'
        user = User.objects.create_superuser(email, display_name, password)

        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, email)
        self.assertEqual(user.display_name, display_name)

    @raises(TypeError)
    def test_without_password(self):
        email = 'bla@example.com'
        display_name = 'superuser'
        User.objects.create_superuser(email, display_name)

        self.assertTrue(True)


class TestCreateUser(TestCase):
    def test(self):
        email = 'bla@example.com'
        display_name = 'user'
        password = 'password'
        user = User.objects.create_user(email, display_name, password)

        self.assertFalse(user.is_superuser)
        self.assertEqual(user.email, email)
        self.assertEqual(user.display_name, display_name)

    def test_without_password(self):
        email = 'bla@example.com'
        display_name = 'user'
        user = User.objects.create_user(email, display_name)

        self.assertFalse(user.is_superuser)
        self.assertEqual(user.email, email)
        self.assertEqual(user.display_name, display_name)

    @raises(TypeError)
    def test_without_display_name(self):
        email = 'bla@example.com'
        password = 'password'
        User.objects.create_user(email, password=password)
