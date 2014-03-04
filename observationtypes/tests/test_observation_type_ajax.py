import json

from django.test import TestCase

from projects.tests.model_factories import UserF, UserGroupF, ProjectF

from ..models import ObservationType

from .model_factories import (
    TextFieldFactory, NumericFieldFactory, DateTimeFieldFactory,
    TrueFalseFieldFactory, LookupFieldFactory, LookupValueFactory,
    FieldFactory, ObservationTypeFactory
)


class ObservationtypeAjaxTest(TestCase):
    def setUp(self):
        self.admin = UserF.create(**{'password': '1'})
        self.contributor = UserF.create(**{'password': '1'})
        self.non_member = UserF.create(**{'password': '1'})

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })

        self.active_type = ObservationTypeFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def _put(self, url, data, user):
        self.client.login(username=user.username, password='1')
        return self.client.put(
            url,
            json.dumps(data),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    def test_update_wrong_status(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id),
            {'status': 'bockwurst'},
            self.admin
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )

    def test_update_description_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id),
            {'description': 'new description'},
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            'new description'
        )

    def test_update_status_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id),
            {'status': 'inactive'},
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            'inactive'
        )

    def test_update_description_with_contributor(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id),
            {'description': 'new description'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            self.active_type.description
        )

    def test_update_status_with_contributor(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id),
            {'status': 'inactive'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )

    def test_update_description_with_non_member(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id),
            {'description': 'new description'},
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            self.active_type.description
        )

    def test_update_status_with_contributor_non_member(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id),
            {'status': 'inactive'},
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )
