from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from rest_framework.test import APIRequestFactory, force_authenticate

from users.tests.model_factories import UserF
from users.models import User
from projects.tests.model_factories import ProjectF

from ..views import (
    ProjectsList,
    ManageSuperUsers,
    AddSuperUsersAjaxView,
    DeleteSuperUsersAjaxView
)


class ProjectsListTest(TestCase):
    def test_get_context_data(self):
        user = UserF.create(**{'is_superuser': True})
        ProjectF.create_batch(5, add_admins=[user])
        ProjectF.create_batch(5)
        view = ProjectsList()
        context = view.get_context_data()
        self.assertEqual(len(context.get('projects')), 10)

    def test_get_with_superuser(self):
        view = ProjectsList.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_user(self):
        view = ProjectsList.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': False})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Superuser tools are for superusers only. You are not a superuser.'
        )

    def test_get_with_anonymous(self):
        view = ProjectsList.as_view()
        url = reverse('admin:superuser_index')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class ManageSuperUsersTest(TestCase):
    def test_get_context_data(self):
        UserF.create_batch(2, **{'is_superuser': True})
        UserF.create_batch(2, **{'is_superuser': False})
        view = ManageSuperUsers()
        context = view.get_context_data()
        self.assertEqual(len(context.get('superusers')), 2)

    def test_get_with_superuser(self):
        view = ManageSuperUsers.as_view()
        url = reverse('admin:superuser_manage_users')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': True})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_user(self):
        view = ManageSuperUsers.as_view()
        url = reverse('admin:superuser_manage_users')
        request = APIRequestFactory().get(url)
        request.user = UserF.create(**{'is_superuser': False})
        response = view(request).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Superuser tools are for superusers only. You are not a superuser.'
        )

    def test_get_with_anonymous(self):
        view = ManageSuperUsers.as_view()
        url = reverse('admin:superuser_manage_users')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class AddSuperUsersAjaxViewTest(TestCase):
    def test_post_with_superuser(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': True})
        user_to_add = UserF.create(**{'is_superuser': False})
        request = factory.post(
            reverse('ajax:superusers_adduser'),
            {'userId': user_to_add.id}
        )
        force_authenticate(request, user=user)
        view = AddSuperUsersAjaxView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 2)

    def test_post_with_user(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': False})
        user_to_add = UserF.create(**{'is_superuser': False})
        request = factory.post(
            reverse('ajax:superusers_adduser'),
            {'userId': user_to_add.id}
        )
        force_authenticate(request, user=user)
        view = AddSuperUsersAjaxView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 0)

    def test_post_non_existing_user(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': True})
        request = factory.post(
            reverse('ajax:superusers_adduser'),
            {'userId': 78463857934859}
        )
        force_authenticate(request, user=user)
        view = AddSuperUsersAjaxView.as_view()
        response = view(request).render()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 1)


class DeleteSuperUsersAjaxViewTest(TestCase):
    def test_delete_with_superuser(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': True})
        user_to_remove = UserF.create(**{'is_superuser': True})
        request = factory.delete(
            reverse('ajax:superusers_deleteuser', kwargs={
                'user_id': user_to_remove.id
            })
        )
        force_authenticate(request, user=user)
        view = DeleteSuperUsersAjaxView.as_view()
        response = view(request, user_id=user_to_remove.id).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 1)

    def test_delete_with_user(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': False})
        user_to_remove = UserF.create(**{'is_superuser': True})
        request = factory.delete(
            reverse('ajax:superusers_deleteuser', kwargs={
                'user_id': user_to_remove.id
            })
        )
        force_authenticate(request, user=user)
        view = DeleteSuperUsersAjaxView.as_view()
        response = view(request, user_id=user_to_remove.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 1)

    def test_delete_not_existing_user(self):
        factory = APIRequestFactory()
        user = UserF.create(**{'is_superuser': True})
        request = factory.delete(
            reverse('ajax:superusers_deleteuser', kwargs={
                'user_id': 84774358734
            })
        )
        force_authenticate(request, user=user)
        view = DeleteSuperUsersAjaxView.as_view()
        response = view(request, user_id=84774358734).render()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(User.objects.filter(is_superuser=True)), 1)
