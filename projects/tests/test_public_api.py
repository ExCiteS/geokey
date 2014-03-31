import json

from django.test import TestCase

from provider.oauth2.models import Client as OAuthClient

from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory
)

from .model_factories import UserF, UserGroupF, ProjectF


class ProjectPublicApiTest(TestCase):
    def setUp(self):
        self.creator = UserF.create(**{'password': '1'})
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})
        self.view_member = UserF.create(**{'password': '1'})

        self.public_project = ProjectF.create(**{
            'isprivate': False,
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.public_project
            })
        })

        self.private_project = ProjectF.create(**{
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.private_project
            })
        })
        observationtype = ObservationTypeFactory(**{
            'status': 'active',
            'project': self.private_project
        })
        TextFieldFactory.create(**{
            'key': 'key_1',
            'observationtype': observationtype
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'observationtype': observationtype
        })

        self.inactive_project = ProjectF.create(**{
            'status': 'inactive',
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.inactive_project
            })
        })

        self.deleted_project = ProjectF.create(**{
            'status': 'deleted',
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.deleted_project
            })
        })

        self.private_everyone_project = ProjectF.create(**{
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
            'everyonecontributes': True
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.private_everyone_project
            })
        })

        self.public_everyone_project = ProjectF.create(**{
            'isprivate': False,
            'creator': self.creator,
            'admins': UserGroupF(add_users=[self.creator, self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
            'everyonecontributes': True
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.public_everyone_project
            })
        })

        self.oauth = OAuthClient.objects.create(
            user=self.admin, name="Test App", client_type=1,
            url="http://ucl.ac.uk"
        )

    def _get(self, url, user):
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
        return self.client.get(url, **auth_headers)

    def test_get_projects_with_admin(self):
        response = self._get('/api/projects', self.admin)
        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 4)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_contributor(self):
        response = self._get('/api/projects', self.contributor)
        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 4)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_view_member(self):
        response = self._get('/api/projects', self.view_member)
        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 4)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_non_member(self):
        response = self._get('/api/projects', self.non_member)
        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 2)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)
        self.assertNotContains(response, self.private_project.name)

    def test_get_deleted_project_with_admin(self):
        response = self._get(
            '/api/projects/' + str(self.deleted_project.id),
            self.admin
        )
        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_admin(self):
        response = self._get(
            '/api/projects/' + str(self.private_project.id),
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.private_project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_inactive_project_with_admin(self):
        response = self._get(
            '/api/projects/' + str(self.inactive_project.id),
            self.admin
        )
        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_admin(self):
        response = self._get(
            '/api/projects/' + str(self.public_project.id),
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.public_project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_deleted_project_with_contributor(self):
        response = self._get(
            '/api/projects/' + str(self.deleted_project.id),
            self.contributor
        )
        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_contributor(self):
        response = self._get(
            '/api/projects/' + str(self.private_project.id),
            self.contributor
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.private_project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_inactive_project_with_contributor(self):
        response = self._get(
            '/api/projects/' + str(self.inactive_project.id),
            self.contributor
        )
        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_contributor(self):
        response = self._get(
            '/api/projects/' + str(self.public_project.id),
            self.contributor
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.public_project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_deleted_project_with_view_member(self):
        response = self._get(
            '/api/projects/' + str(self.deleted_project.id),
            self.view_member
        )
        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_view_member(self):
        response = self._get(
            '/api/projects/' + str(self.private_project.id),
            self.view_member
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.private_project.name)
        self.assertContains(response, '"can_contribute": false')

    def test_get_inactive_project_with_view_member(self):
        response = self._get(
            '/api/projects/' + str(self.inactive_project.id),
            self.view_member
        )
        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_view_member(self):
        response = self._get(
            '/api/projects/' + str(self.public_project.id),
            self.view_member
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.public_project.name)
        self.assertContains(response, '"can_contribute": false')

    def test_get_deleted_project_with_non_member(self):
        response = self._get(
            '/api/projects/' + str(self.deleted_project.id),
            self.non_member
        )
        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_non_member(self):
        response = self._get(
            '/api/projects/' + str(self.private_project.id),
            self.non_member
        )
        self.assertEqual(response.status_code, 403)

    def test_get_inactive_project_with_non_member(self):
        response = self._get(
            '/api/projects/' + str(self.inactive_project.id),
            self.non_member
        )
        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_non_member(self):
        response = self._get(
            '/api/projects/' + str(self.public_project.id),
            self.non_member
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.public_project.name)
        self.assertContains(response, '"can_contribute": false')
