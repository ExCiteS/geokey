from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from rest_framework.test import APIRequestFactory

from users.tests.model_factories import UserF
from projects.tests.model_factories import ProjectF

from ..views import ProjectsList


class ProjectsListTest(TestCase):
    def test_get_context_data(self):
        user = UserF.create(**{'is_superuser': True})
        ProjectF.create_batch(5, add_admins=[user])
        ProjectF.create_batch(5)
        view = ProjectsList.as_view()
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
