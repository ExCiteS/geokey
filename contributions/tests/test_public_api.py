import json

from django.test import TestCase

from provider.oauth2.models import Client as OAuthClient

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory
)
from contributions.models import Observation

from .model_factories import LocationFactory


class ProjectPublicApiTest(TestCase):
    def setUp(self):
        self.observationtype = ObservationTypeFactory(**{
            'status': 'active'
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

        self.update_data = {
            "properties": {
                "key_2": 15,
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

    def _put(self, url, data, user):
        auth_headers = self._get_auth_headers(user)
        return self.client.put(
            url,
            json.dumps(data),
            content_type='application/json', **auth_headers
        )

    def _post(self, url, data, user):
        auth_headers = self._get_auth_headers(user)
        return self.client.post(
            url,
            json.dumps(data),
            content_type='application/json', **auth_headers
        )

    def _delete(self, url, user):
        auth_headers = self._get_auth_headers(user)
        return self.client.delete(
            url,
            content_type='application/json', **auth_headers
        )

    def test_contribute_with_wrong_observation_type(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        self.observationtype.project = project
        self.observationtype.save()
        self.data['properties']['observationtype'] = 3864

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            admin
        )
        self.assertEqual(response.status_code, 400)

    def test_contribute_with_invalid(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        self.observationtype.project = project
        self.observationtype.save()
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
            '/api/projects/' + str(project.id) + '/observations',
            data,
            admin
        )
        self.assertEqual(response.status_code, 400)

    def test_contribute_to_public_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'isprivate': False,
            'admins': UserGroupF(add_users=[admin])
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            admin
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_with_contributor(self):
        contributor = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'isprivate': False,
            'contributors': UserGroupF(add_users=[contributor])
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            contributor
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_with_view_member(self):
        view_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'isprivate': False
        })
        self.observationtype.project = project

        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': project
            })
        })
        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            view_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_public_with_non_member(self):
        non_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'isprivate': False
        })
        self.observationtype.project = project

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            non_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_public_everyone_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'isprivate': False,
            'everyonecontributes': True,
            'admins': UserGroupF(add_users=[admin])
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            admin
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_everyone_with_contributor(self):
        contributor = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'isprivate': False,
            'everyonecontributes': True,
            'contributors': UserGroupF(add_users=[contributor])
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            contributor
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_everyone_with_view_member(self):
        view_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'isprivate': False,
            'everyonecontributes': True
        })
        self.observationtype.project = project
        self.observationtype.save()

        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': project
            })
        })
        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            view_member
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_public_everyone_with_non_member(self):
        non_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'isprivate': False,
            'everyonecontributes': True
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            non_member
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_private_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            admin
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_private_with_contributor(self):
        contributor = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[contributor])
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            contributor
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_private_with_view_member(self):
        view_member = UserF.create(**{'password': '1'})
        project = ProjectF.create()
        self.observationtype.project = project

        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': project
            })
        })
        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            view_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_private_with_non_member(self):
        non_member = UserF.create(**{'password': '1'})
        project = ProjectF.create()
        self.observationtype.project = project

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            non_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_private_everyone_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin]),
            'everyonecontributes': True
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            admin
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_private_everyone_with_contributor(self):
        contributor = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[contributor]),
            'everyonecontributes': True
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            contributor
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_private_everyone_with_view_member(self):
        view_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'everyonecontributes': True
        })
        self.observationtype.project = project
        self.observationtype.save()

        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': project
            })
        })
        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            view_member
        )
        self.assertEqual(response.status_code, 201)

    def test_contribute_to_private_everyone_with_non_member(self):
        non_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'everyonecontributes': True
        })
        self.observationtype.project = project

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            non_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_inactive_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin]),
            'status': 'inactive'
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            admin
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_inactive_with_contributor(self):
        contributor = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[contributor]),
            'status': 'inactive'
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            contributor
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_inactive_with_view_member(self):
        view_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'status': 'inactive'
        })
        self.observationtype.project = project
        self.observationtype.save()

        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': project
            })
        })
        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            view_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_inactive_with_non_member(self):
        non_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'status': 'inactive'
        })
        self.observationtype.project = project

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            non_member
        )
        self.assertEqual(response.status_code, 403)

    def test_contribute_to_deleted_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin]),
            'status': 'deleted'
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            admin
        )
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_contributor(self):
        contributor = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[contributor]),
            'status': 'deleted'
        })
        self.observationtype.project = project
        self.observationtype.save()

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            contributor
        )
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_view_member(self):
        view_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'status': 'deleted'
        })
        self.observationtype.project = project
        self.observationtype.save()

        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': project
            })
        })
        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            view_member
        )
        self.assertEqual(response.status_code, 404)

    def test_contribute_to_deleted_with_non_member(self):
        non_member = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'status': 'deleted'
        })
        self.observationtype.project = project

        response = self._post(
            '/api/projects/' + str(project.id) + '/observations',
            self.data,
            non_member
        )
        self.assertEqual(response.status_code, 404)

    def test_update_to_public_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        self.observationtype.project = project
        self.observationtype.save()

        location = LocationFactory()

        TextFieldFactory(**{
            'key': 'key_1',
            'observationtype': self.observationtype
        })
        NumericFieldFactory(**{
            'key': 'key_2',
            'observationtype': self.observationtype
        })
        observation = Observation.create(
            data={
                "key_1": "value 1",
                "key_2": 12,
            },
            observationtype=self.observationtype,
            project=project,
            location=location,
            creator=admin
        )

        response = self._put(
            '/api/projects/' + str(project.id) +
            '/observations/' + str(observation.id),
            self.update_data,
            admin
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_to_public_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        self.observationtype.project = project
        self.observationtype.save()

        location = LocationFactory()

        TextFieldFactory(**{
            'key': 'key_1',
            'observationtype': self.observationtype
        })
        NumericFieldFactory(**{
            'key': 'key_2',
            'observationtype': self.observationtype
        })
        observation = Observation.create(
            data={
                "key_1": "value 1",
                "key_2": 12,
            },
            observationtype=self.observationtype,
            project=project,
            location=location,
            creator=admin
        )

        response = self._delete(
            '/api/projects/' + str(project.id) +
            '/observations/' + str(observation.id),
            admin
        )
        self.assertEqual(response.status_code, 204)
