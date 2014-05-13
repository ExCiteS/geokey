from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from nose.tools import raises

from projects.tests.model_factories import ProjectF, UserF, UserGroupF

from ..models import View
from ..views import ViewUpdate

from .model_factories import ViewFactory, ViewGroupFactory


class ViewAjaxTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        self.view = ViewFactory(**{
            'project': self.project,
            'description': 'description'
        })

    def _put(self, data, user):
        url = reverse('api:single_view', kwargs={
            'project_id': self.project.id,
            'view_id': self.view.id
        })
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        theview = ViewUpdate.as_view()
        return theview(
            request,
            project_id=self.project.id,
            view_id=self.view.id).render()

    def _delete(self, user):
        url = reverse('api:single_view', kwargs={
            'project_id': self.project.id,
            'view_id': self.view.id
        })
        request = self.factory.delete(url)
        force_authenticate(request, user=user)
        theview = ViewUpdate.as_view()
        return theview(
            request,
            project_id=self.project.id,
            view_id=self.view.id).render()

    def test_update_description_with_admin(self):
        response = self._put({'description': 'bockwurst'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(View.objects.get(pk=self.view.id).description, 'bockwurst')

    def test_update_description_with_contributor(self):
        response = self._put({'description': 'bockwurst'}, self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).description, 'description')

    def test_update_description_with_non_member(self):
        response = self._put({'description': 'bockwurst'}, self.non_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).description, 'description')

    def test_update_description_with_view_member(self):
        view_member = UserF.create()
        ViewGroupFactory(add_users=[view_member], **{
            'view': self.view
        })

        response = self._put({'description': 'bockwurst'}, view_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).description, 'description')

    @raises(View.DoesNotExist)
    def test_delete_with_admin(self):
        response = self._delete(self.admin)
        self.assertEqual(response.status_code, 204)
        View.objects.get(pk=self.view.id)

    def test_delete_with_contributor(self):
        response = self._delete(self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).status, 'active')

    def test_delete_with_non_member(self):
        response = self._delete(
            self.non_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).status, 'active')

    def test_delete_with_view_member(self):
        view_member = UserF.create()
        ViewGroupFactory(add_users=[view_member], **{
            'view': self.view
        })

        response = self._delete(
            view_member
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(View.objects.get(pk=self.view.id).status, 'active')
