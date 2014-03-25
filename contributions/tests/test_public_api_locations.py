import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from provider.oauth2.models import Client as OAuthClient

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory

from .model_factories import LocationFactory


class LocationApiTest(TestCase):
    def setUp(self):
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.view_member = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
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

        self.oauth = OAuthClient.objects.create(
            user=self.admin, name="Test App", client_type=1,
            url="http://ucl.ac.uk"
        )

    def _get(self, user):
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
            'api:project_locations',
            kwargs={
                'project_id': self.project.id
            }
        )
        return self.client.get(url, **auth_headers)

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
