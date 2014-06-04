import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF

from .model_factories import LocationFactory
from ..views import Locations, SingleLocation
from ..models import Location


class LocationApiTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view_member = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member]
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


class LocationUpdateApiTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view_member = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member]
        )

        self.location = LocationFactory(**{
            'private': True,
            'private_for_project': self.project
        })

    def _put(self, data, user, location_id=None):
        l_id = location_id or self.location.id
        url = reverse(
            'api:project_single_location',
            kwargs={
                'project_id': self.project.id,
                'location_id': l_id
            }
        )
        request = self.factory.put(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = SingleLocation.as_view()
        return view(
            request, project_id=self.project.id, location_id=l_id).render()
        return self.client.put(
            url,
            json.dumps(data),
            content_type='application/json'
        )

    def test_update_location_with_wrong_status(self):
        response = self._put({'status': 'Bla'}, self.admin)
        self.assertEqual(response.status_code, 400)

        location = Location.objects.get(pk=self.location.id)
        self.assertEqual(location.status, self.location.status)

    def test_update_not_existing_location(self):
        response = self._put(
            {'properties': {'name': 'UCL'}},
            self.admin,
            location_id=10000000000000000000000
        )
        self.assertEqual(response.status_code, 404)

    def test_update_private_location(self):
        private = LocationFactory(**{
            'private': True
        })
        response = self._put(
            {'name': 'UCL'}, self.admin, location_id=private.id)
        self.assertEqual(response.status_code, 403)

        location = Location.objects.get(pk=private.id)
        self.assertEqual(location.name, private.name)

    def test_update_location_with_admin(self):
        response = self._put(
            {
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        -0.14061212539672852,
                        51.501763857255106
                    ]
                },
                'name': 'UCL'
            },
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        location = Location.objects.get(pk=self.location.id)
        self.assertEqual(location.name, 'UCL')

    def test_update_location_with_contributor(self):
        response = self._put({'description': 'main quad'}, self.contributor)
        self.assertEqual(response.status_code, 200)

        location = Location.objects.get(pk=self.location.id)
        self.assertEqual(location.description, 'main quad')

    def test_update_location_with_view_member(self):
        response = self._put({'description': 'UCL'}, self.view_member)
        self.assertEqual(response.status_code, 403)

        location = Location.objects.get(pk=self.location.id)
        self.assertEqual(location.description, self.location.description)

    def test_update_location_with_non_member(self):
        response = self._put({'description': 'UCL'}, self.non_member)
        self.assertEqual(response.status_code, 403)

        location = Location.objects.get(pk=self.location.id)
        self.assertEqual(location.description, self.location.description)
