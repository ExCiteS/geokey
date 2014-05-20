from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF

from .model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory,
    LookupFieldFactory, LookupValueFactory
)

from ..models import Field
from ..views import FieldUpdate, FieldLookupsUpdate, FieldLookups


class UpdateFieldTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.observationtype = ObservationTypeFactory(**{
            'project': self.project,
            'status': 'active'
        })

        self.field = TextFieldFactory(**{
            'observationtype': self.observationtype
        })

    def _put(self, data, user):
        url = reverse(
            'ajax:observationtype_field',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.observationtype.id,
                'field_id': self.field.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = FieldUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            observationtype_id=self.observationtype.id,
            field_id=self.field.id
        ).render()

    def test_update_non_existing_field(self):
        url = reverse(
            'ajax:observationtype_field',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.observationtype.id,
                'field_id': 554454545
            }
        )
        request = self.factory.put(url, {'description': 'new description'})
        force_authenticate(request, user=self.admin)
        view = FieldUpdate.as_view()
        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=self.observationtype.id,
            field_id=554454545
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_update_description_with_admin(self):
        response = self._put({'description': 'new description'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).description,
            'new description'
        )

    def test_update_required_with_admin(self):
        response = self._put({'required': True}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).required
        )

    def test_update_status_with_admin(self):
        response = self._put({'status': 'inactive'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).status,
            'inactive'
        )

    def test_update_status_with_contributor(self):
        response = self._put({'status': 'inactive'}, self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).status,
            'active'
        )

    def test_update_status_with_non_member(self):
        response = self._put({'status': 'inactive'}, self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).status,
            'active'
        )

    def test_update_wrong_status_with_admin(self):
        response = self._put({'status': 'bla'}, self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).status,
            'active'
        )


class UpdateNumericField(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.observationtype = ObservationTypeFactory(**{
            'project': self.project,
            'status': 'active'
        })

        self.field = NumericFieldFactory(**{
            'observationtype': self.observationtype
        })

    def _put(self, data, user):
        url = reverse(
            'ajax:observationtype_field',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.observationtype.id,
                'field_id': self.field.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = FieldUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            observationtype_id=self.observationtype.id,
            field_id=self.field.id
        ).render()

    def test_update_numericfield_minval_with_admin(self):
        response = self._put({'minval': 12}, self.admin)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).minval, 12
        )

    def test_update_numericfield_maxval_with_admin(self):
        response = self._put({'maxval': 12}, self.admin)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).maxval, 12
        )

    def test_update_numericfield_minval_maxval_with_admin(self):
        response = self._put({'maxval': 12, 'minval': 3}, self.admin)

        self.assertEqual(response.status_code, 200)
        field = Field.objects.get_single(
            self.admin, self.project.id, self.observationtype.id,
            self.field.id
        )
        self.assertEqual(field.minval, 3)
        self.assertEqual(field.maxval, 12)

    def test_update_numericfield_description_with_admin(self):
        response = self._put({'description': 'new description'}, self.admin)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.observationtype.id,
                self.field.id).description, 'new description'
        )


class AddLookupValueTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.active_type = ObservationTypeFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def test_add_lookupvalue_with_admin(self):
        lookup_field = LookupFieldFactory(**{
            'observationtype': self.active_type
        })

        url = reverse(
            'ajax:observationtype_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.active_type.id,
                'field_id': lookup_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=self.active_type.id,
            field_id=lookup_field.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 1)

    def test_add_lookupvalue_to_not_existing_field(self):
        url = reverse(
            'ajax:observationtype_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.active_type.id,
                'field_id': 32874893274
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=self.active_type.id,
            field_id=32874893274
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_add_lookupvalue_to_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'observationtype': self.active_type
        })
        url = reverse(
            'ajax:observationtype_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.active_type.id,
                'field_id': num_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=self.active_type.id,
            field_id=num_field.id
        ).render()
        self.assertEqual(response.status_code, 404)


class RemoveLookupValues(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.active_type = ObservationTypeFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def test_remove_lookupvalue_with_admin(self):
        lookup_field = LookupFieldFactory(**{
            'observationtype': self.active_type
        })
        lookup_value = LookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:observationtype_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            len(lookup_field.lookupvalues.filter(status='active')), 0
        )

    def test_remove_lookupvalue_from_not_existing_field(self):
        lookup_value = LookupValueFactory()

        url = reverse(
            'ajax:observationtype_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.active_type.id,
                'field_id': 45455,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=self.active_type.id,
            field_id=45455,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_not_exisiting_lookupvalue(self):
        lookup_field = LookupFieldFactory(**{
            'observationtype': self.active_type
        })

        url = reverse(
            'ajax:observationtype_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_lookupvalue_from_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'observationtype': self.active_type
        })

        url = reverse(
            'ajax:observationtype_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'observationtype_id': self.active_type.id,
                'field_id': num_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            observationtype_id=self.active_type.id,
            field_id=num_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)
