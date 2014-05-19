import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory

from .model_factories import LocationFactory
from ..views import Locations


class LocationApiTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view_member = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.other_project = ProjectF.create()

        # Create 20 locations, 10 should be accessible for the project
        for x in range(0, 5):
            LocationFactory()
            LocationFactory(**{
                'private': True,
                'private_for_project': self.other_project
            })
            LocationFactory(**{
                'private': True,
                'private_for_project': self.project
            })
            LocationFactory(**{
                'private': True
            })

        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })

    def _get(self, user):
        url = reverse(
            'api:project_locations',
            kwargs={
                'project_id': self.project.id
            }
        )
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        view = Locations.as_view()
        return view(request, project_id=self.project.id).render()

    def test_get_locations_with_admin(self):
        response = self._get(self.admin)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            len(json.loads(response.content).get('features')), 10
        )

    def test_get_locations_with_contributor(self):
        response = self._get(self.contributor)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            len(json.loads(response.content).get('features')), 10
        )

    def test_get_locations_with_view_member(self):
        response = self._get(self.view_member)
        self.assertEquals(response.status_code, 403)

    def test_get_locations_with_non_member(self):
        response = self._get(self.non_member)
        self.assertEquals(response.status_code, 403)
