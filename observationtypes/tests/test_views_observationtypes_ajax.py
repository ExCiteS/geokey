from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, UserGroupF, ProjectF

from ..models import ObservationType
from ..views import ObservationTypeApiDetail

from .model_factories import ObservationTypeFactory


class ObservationtypeAjaxTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })

        self.active_type = ObservationTypeFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def _put(self, data, user):
        url = reverse(
            'ajax:project_observationtype',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.active_type.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = ObservationTypeApiDetail.as_view()
        return view(
            request,
            project_id=self.project.id,
            observationtype_id=self.active_type.id
        ).render()

    def test_update_not_existing_type(self):
        url = reverse(
            'ajax:project_observationtype',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': 2376
            }
        )
        request = self.factory.put(url, {'status': 'inactive'})
        force_authenticate(request, user=self.admin)
        view = ObservationTypeApiDetail.as_view()
        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=2376
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_update_wrong_status(self):
        response = self._put({'status': 'bockwurst'}, self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )

    def test_update_description_with_admin(self):
        response = self._put({'description': 'new description'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            'new description'
        )

    def test_update_status_with_admin(self):
        response = self._put({'status': 'inactive'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            'inactive'
        )

    def test_update_description_with_contributor(self):
        response = self._put(
            {'description': 'new description'}, self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            self.active_type.description
        )

    def test_update_status_with_contributor(self):
        response = self._put(
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
            {'status': 'inactive'},
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            ObservationType.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )
