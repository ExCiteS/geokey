"""Tests for views of contributions (locations)."""

import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from geokey.projects.tests.model_factories import UserFactory, ProjectFactory

from ..model_factories import LocationFactory
from geokey.contributions.views.locations import (
    LocationsAPIView,
    SingleLocationAPIView
)
from geokey.contributions.models import Location


class LocationApiTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.other_project = ProjectFactory.create()

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
        view = LocationsAPIView.as_view()
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

    def test_get_locations_with_non_member(self):
        response = self._get(self.non_member)
        self.assertEquals(response.status_code, 404)


class LocationQueryTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.project = ProjectFactory()
        LocationFactory.create(**{'name': 'Hyde Park'})
        LocationFactory.create(**{'description': 'hyde'})
        LocationFactory.create(**{'name': 'hyde park'})
        LocationFactory.create(**{'name': 'Regents Park'})

        self.url = reverse(
            'api:project_locations',
            kwargs={
                'project_id': self.project.id
            }
        )

    def test_hyd(self):
        request = self.factory.get(self.url + '?query=Hyd')
        force_authenticate(request, user=self.project.creator)
        view = LocationsAPIView.as_view()
        response = view(request, project_id=self.project.id).render()

        response_json = json.loads(response.content)
        self.assertEqual(len(response_json.get('features')), 3)
        self.assertNotIn('Regents Park', response.content)

    def test_park(self):
        request = self.factory.get(self.url + '?query=park')
        force_authenticate(request, user=self.project.creator)
        view = LocationsAPIView.as_view()
        response = view(request, project_id=self.project.id).render()

        response_json = json.loads(response.content)
        self.assertEqual(len(response_json.get('features')), 3)
        self.assertNotIn('"description": "hyde"', response.content)

    def test_regen(self):
        request = self.factory.get(self.url + '?query=regen')
        force_authenticate(request, user=self.project.creator)
        view = LocationsAPIView.as_view()
        response = view(request, project_id=self.project.id).render()

        response_json = json.loads(response.content)
        self.assertEqual(len(response_json.get('features')), 1)
        self.assertNotIn('hyde', response.content)
        self.assertNotIn('Hyde Park', response.content)


class LocationUpdateApiTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.view_member = UserFactory.create()
        self.non_member = UserFactory.create()

        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.location = LocationFactory(**{
            'private': True,
            'private_for_project': self.project
        })

    def patch(self, data, user, location_id=None):
        l_id = location_id or self.location.id
        url = reverse(
            'api:project_single_location',
            kwargs={
                'project_id': self.project.id,
                'location_id': l_id
            }
        )
        request = self.factory.patch(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = SingleLocationAPIView.as_view()
        return view(
            request, project_id=self.project.id, location_id=l_id).render()

    def test_update_location_with_wrong_status(self):
        response = self.patch({'status': 'Bla'}, self.admin)
        self.assertEqual(response.status_code, 400)

        location = Location.objects.get(pk=self.location.id)
        self.assertEqual(location.status, self.location.status)

    def test_update_not_existing_location(self):
        response = self.patch(
            {'properties': {'name': 'UCL'}},
            self.admin,
            location_id=10000000000000000000000
        )
        self.assertEqual(response.status_code, 404)

    def test_update_private_location(self):
        private = LocationFactory(**{
            'private': True
        })
        response = self.patch(
            {'name': 'UCL'}, self.admin, location_id=private.id)
        self.assertEqual(response.status_code, 403)

        location = Location.objects.get(pk=private.id)
        self.assertEqual(location.name, private.name)

    def test_update_location_with_admin(self):
        response = self.patch(
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
        response = self.patch({'description': 'main quad'}, self.contributor)
        self.assertEqual(response.status_code, 200)

        location = Location.objects.get(pk=self.location.id)
        self.assertEqual(location.description, 'main quad')

    def test_update_location_with_non_member(self):
        response = self.patch({'description': 'UCL'}, self.non_member)
        self.assertEqual(response.status_code, 404)

        location = Location.objects.get(pk=self.location.id)
        self.assertEqual(location.description, self.location.description)
