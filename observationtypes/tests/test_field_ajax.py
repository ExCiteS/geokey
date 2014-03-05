import json

from django.test import TestCase

from projects.tests.model_factories import UserF, UserGroupF, ProjectF

from .model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory
)

from ..models import Field


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

        self.field = TextFieldFactory(**{
            'observationtype': self.active_type
        })

    def _put(self, url, data, user):
        self.client.login(username=user.username, password='1')
        return self.client.put(
            url,
            json.dumps(data),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )

    def test_update_description_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(self.field.id),
            {'description': 'new description'},
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                self.field.id).description,
            'new description'
        )

    def test_update_required_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(self.field.id),
            {'required': True},
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                self.field.id).required
        )

    def test_update_status_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(self.field.id),
            {'status': 'inactive'},
            self.admin
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                self.field.id).status,
            'inactive'
        )

    def test_update_status_with_contributor(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(self.field.id),
            {'status': 'inactive'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                self.field.id).status,
            'active'
        )

    def test_update_status_with_non_member(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(self.field.id),
            {'status': 'inactive'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                self.field.id).status,
            'active'
        )

    def test_update_wrong_status_with_admin(self):
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(self.field.id),
            {'status': 'bla'},
            self.admin
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                self.field.id).status,
            'active'
        )

    def test_update_numericfield_minval_with_admin(self):
        num_field = NumericFieldFactory(**{
            'observationtype': self.active_type
        })
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(num_field.id),
            {'minval': 12},
            self.admin
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                num_field.id).minval, 12
        )

    def test_update_numericfield_maxval_with_admin(self):
        num_field = NumericFieldFactory(**{
            'observationtype': self.active_type
        })
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(num_field.id),
            {'maxval': 12},
            self.admin
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                num_field.id).maxval, 12
        )

    def test_update_numericfield_minval_maxval_with_admin(self):
        num_field = NumericFieldFactory(**{
            'observationtype': self.active_type
        })
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(num_field.id),
            {'maxval': 12, 'minval': 3},
            self.admin
        )

        self.assertEqual(response.status_code, 200)
        field = Field.objects.get_single(
            self.admin, self.project.id, self.active_type.id, num_field.id)
        self.assertEqual(field.minval, 3)
        self.assertEqual(field.maxval, 12)

    def test_update_numericfield_description_with_admin(self):
        num_field = NumericFieldFactory(**{
            'observationtype': self.active_type
        })
        response = self._put(
            '/ajax/projects/' + str(self.project.id) + '/observationtypes/' +
            str(self.active_type.id) + '/fields/' + str(num_field.id),
            {'description': 'new description'},
            self.admin
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.active_type.id,
                num_field.id).description, 'new description'
        )
