from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF

from ..views import ProjectObersvationsView


class TestDataViewsPublicApi(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member]
        )

    def get(self, user):
        url = reverse('api:project_all_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        theview = ProjectObersvationsView.as_view()
        return theview(
            request,
            project_id=self.project.id).render()

    def test_get_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, 200)

    def test_get_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, 403)

    def test_get_with_view_member(self):
        response = self.get(self.view_member)
        self.assertEqual(response.status_code, 403)

    def test_get_with_some_dude(self):
        some_dude = UserF.create()
        response = self.get(some_dude)
        self.assertEqual(response.status_code, 403)
