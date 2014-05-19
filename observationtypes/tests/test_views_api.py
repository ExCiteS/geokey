from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF

from .model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory,
    LookupFieldFactory, LookupValueFactory
)

from ..views import SingleObservationType


class ObservationTypePublicApiTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_member = UserF.create()

        self.project = ProjectF.create(
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

    def _get(self, user):
        url = reverse(
            'api:observationtype',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.observationtype.id
            }
        )
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        view = SingleObservationType.as_view()
        return view(
            request,
            project_id=self.project.id,
            observationtype_id=self.observationtype.id
        ).render()

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
