import json

from django.test import TestCase

from provider.oauth2.models import Client as OAuthClient

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory
)


class ProjectPublicApiTest(TestCase):
    def setUp(self):
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.view_member = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.observationtype = ObservationTypeFactory(**{
            'status': 'active',
            'project': self.project
        })

        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })

        TextFieldFactory.create(**{
            'key': 'key_1',
            'observationtype': self.observationtype
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'observationtype': self.observationtype
        })

        self.oauth = OAuthClient.objects.create(
            user=UserF.create(), name="Test App", client_type=1,
            url="http://ucl.ac.uk"
        )

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
                "observationtype": self.observationtype.id,
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
            }
        }

    def _get_auth_headers(self, user):
        token = self.client.post(
            '/oauth2/access_token/',
            {
                "client_id": self.oauth.client_id,
                "client_secret": self.oauth.client_secret,
                "grant_type": "password",
                "username": user.username,
                "password": '1'
            }
        )
        return {
            'HTTP_AUTHORIZATION': 'Bearer '
            '' + json.loads(token.content).get('access_token'),
        }

    def _post(self, url, data, user):
        auth_headers = self._get_auth_headers(user)
        return self.client.post(
            url,
            json.dumps(data),
            content_type='application/json', **auth_headers
        )

    def test_contribute_with_wrong_observation_type(self):
        self.data['properties']['observationtype'] = 3864

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.admin
        )
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
                "location": {
                    "name": "UCL",
                    "description": "UCL's main quad",
                    "private": True
                },
                "observationtype": self.observationtype.id,
                "data": {
                    "key_1": "value 1",
                    "key_2": "jsdbdjhsb"
                }
            }
        }
        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            data,
            self.admin
        )
        self.assertEqual(response.status_code, 400)

    def test_contribute_to_public_with_admin(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.admin
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_with_contributor(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.contributor
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_with_view_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.view_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_public_with_non_member(self):
        self.project.isprivate = False
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.non_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_public_everyone_with_admin(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.admin
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_everyone_with_contributor(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.contributor
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_everyone_with_view_member(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.view_member
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_everyone_with_non_member(self):
        self.project.isprivate = False
        self.project.everyonecontributes = True
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.non_member
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_with_admin(self):
        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.admin
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_with_contributor(self):
        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.contributor
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_with_view_member(self):
        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.view_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_private_with_non_member(self):
        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_private_everyone_with_admin(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.admin
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_everyone_with_contributor(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.contributor
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_everyone_with_view_member(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.view_member
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.project.observations.all()), 1)

    def test_contribute_to_private_everyone_with_non_member(self):
        self.project.everyonecontributes = True
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_admin(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.admin
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_contributor(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_view_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.view_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_inactive_with_non_member(self):
        self.project.status = 'inactive'
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.project.observations.all()), 0)

    def test_contribute_to_deleted_with_admin(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.admin
        )
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_contributor(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.contributor
        )
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_view_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.view_member
        )
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_non_member(self):
        self.project.status = 'deleted'
        self.project.save()

        response = self._post(
            '/api/projects/' + str(self.project.id) + '/observations',
            self.data,
            self.non_member
        )
        self.assertEqual(response.status_code, 404)
