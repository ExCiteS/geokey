import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from provider.oauth2.models import Client as OAuthClient

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory

from .model_factories import LocationFactory

from ..models import Location


class LocationUpdateApiTest(TestCase):
    def setUp(self):
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.view_member = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })

        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })

        self.location = LocationFactory(**{
            'private': True,
            'private_for_project': self.project
        })

        self.oauth = OAuthClient.objects.create(
            user=self.admin, name="Test App", client_type=1,
            url="http://ucl.ac.uk"
        )

    def _put(self, data, user, location_id=None):
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
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer '
            '' + json.loads(token.content).get('access_token'),
        }
        url = reverse(
            'api:project_single_location',
            kwargs={
                'project_id': self.project.id,
                'location_id': location_id or self.location.id
            }
        )
        return self.client.put(
            url,
            json.dumps(data),
            content_type='application/json',
            **auth_headers
        )

    # def test_update_geomtery(self):
    #     response = self._put({'geometry': 'Bla'}, self.admin)

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
