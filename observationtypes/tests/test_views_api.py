import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from provider.oauth2.models import Client as OAuthClient

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory

from .model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory,
    LookupFieldFactory, LookupValueFactory
)


class ObservationTypePublicApiTest(TestCase):
    def setUp(self):
        self.creator = UserF.create(**{'password': '1'})
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})
        self.view_member = UserF.create(**{'password': '1'})

        self.project = ProjectF.create(**{
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })
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
        self.inactive_field = TextFieldFactory.create(**{
            'key': 'key_3',
            'observationtype': self.observationtype,
            'status': 'inactive'
        })
        lookup_field = LookupFieldFactory(**{
            'key': 'key_4',
            'observationtype': self.observationtype
        })
        LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        LookupValueFactory(**{
            'name': 'Kermit',
            'field': lookup_field
        })
        LookupValueFactory(**{
            'name': 'Gonzo',
            'field': lookup_field,
            'status': 'inactive'
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
            'api:project_observation_types',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.observationtype.id
            }
        )
        return self.client.get(url, **auth_headers)

    def test_get_observationType_with_admin(self):
        response = self._get(self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Gonzo")
        self.assertNotContains(response, self.inactive_field.name)

    def test_get_observationType_with_contributor(self):
        response = self._get(self.contributor)
        self.assertEqual(response.status_code, 200)

    def test_get_observationType_with_view_member(self):
        response = self._get(self.view_member)
        self.assertEqual(response.status_code, 200)

    def test_get_observationType_with_non_member(self):
        response = self._get(self.non_member)
        self.assertEqual(response.status_code, 403)
