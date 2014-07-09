import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory
)

from .model_factories import LocationFactory
from ..views import ProjectObservations


class ProjectPublicApiTest(TestCase):
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
        self.observationtype = ObservationTypeFactory(**{
            'status': 'active',
            'project': self.project
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'observationtype': self.observationtype
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'observationtype': self.observationtype
        })

        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12,
                "contributiontype": self.observationtype.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }

    def _post(self, data, user):
        url = reverse(
            'api:project_observations',
            kwargs={
                'project_id': self.project.id
            }
        )
        request = self.factory.post(
            url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=user)
        view = ProjectObservations.as_view()
        return view(request, project_id=self.project.id).render()

    def test_contribute_with_wrong_observation_type(self):
        self.data['properties']['contributiontype'] = 3864

        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_with_invalid(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": 12,
                "key_2": "jsdbdjhsb",
                "contributiontype": self.observationtype.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_with_existing_location(self):
        location = LocationFactory()
        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "location": {
                    "id": location.id,
                    "name": location.name,
                    "description": location.description,
                    "private": location.private
                },
                "contributiontype": self.observationtype.id,
                "key_1": "value 1",
                "key_2": 12
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 201)

    def test_contribute_with_private_for_project_location(self):
        location = LocationFactory(**{
            'private': True,
            'private_for_project': self.project
        })

        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "location": {
                    "id": location.id,
                    "name": location.name,
                    "description": location.description,
                    "private": location.private
                },
                "contributiontype": self.observationtype.id,
                "key_1": "value 1",
                "key_2": 12
            }
        }
        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 201)

    def test_contribute_with_wrong_project_location(self):
        project = ProjectF()
        location = LocationFactory(**{
            'private': True,
            'private_for_project': project
        })

        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "location": {
                    "id": location.id,
                    "name": location.name,
                    "description": location.description,
                    "private": location.private
                },
                "contributiontype": self.observationtype.id,
                "key_1": "value 1",
                "key_2": 12
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_with_private_location(self):
        location = LocationFactory(**{
            'private': True
        })

        data = {
            "type": "Feature",
            "geometry": location.geometry.geojson,
            "properties": {
                "location": {
                    "id": location.id,
                    "name": location.name,
                    "description": location.description,
                    "private": location.private
                },
                "contributiontype": self.observationtype.id,
                "key_1": "value 1",
                "key_2": 12
            }
        }

        response = self._post(data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_valid_draft(self):
        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": 12,
                "contributiontype": self.observationtype.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
                "status": "draft"
            }
        }
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 201)
        self.assertIn('"status": "draft"', response.content)

    def test_contribute_invalid_draft(self):
        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -0.13404607772827148,
                    51.52439200896907
                ]
            },
            "properties": {
                "key_1": "value 1",
                "key_2": "Blah",
                "contributiontype": self.observationtype.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
                "status": "draft"
            }
        }
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 400)

    def test_contribute_to_public_with_admin(self):
        self.project.isprivate = False
        self.project.save()
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_with_contributor(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(self.data, self.contributor)
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_with_view_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(self.data, self.view_member)
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_public_with_non_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(self.data, self.non_member)
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_private_with_admin(self):
        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_with_contributor(self):
        response = self._post(self.data, self.contributor)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_with_view_member(self):
        response = self._post(self.data, self.view_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_private_with_non_member(self):
        response = self._post(self.data, self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_admin(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_contributor(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(self.data, self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_view_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(self.data, self.view_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_non_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(self.data, self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_deleted_with_admin(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(self.data, self.admin)
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_contributor(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(self.data, self.contributor)
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_view_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(self.data, self.view_member)
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_non_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(self.data, self.non_member)
        self.assertEqual(response.status_code, 404)
