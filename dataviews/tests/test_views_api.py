from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF, UserGroupF

from ..views import SingleView
from .model_factories import ViewFactory, ViewGroupFactory


class TestDataViewsPublicApi(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view_member = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })

    def get(self, view, user):
        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        theview = SingleView.as_view()
        return theview(
            request,
            project_id=view.project.id,
            view_id=view.id).render()

    def test_get_active_view_with_admin(self):
        view = ViewFactory(**{'project': self.project})
        response = self.get(view, self.admin)

        self.assertEquals(response.status_code, 200)

    def test_get_inactive_view_with_admin(self):
        view = ViewFactory(**{
            'project': self.project,
            'status': 'deleted'
        })
        response = self.get(view, self.admin)
        self.assertEquals(response.status_code, 404)

    def test_get_active_view_with_contributor(self):
        view = ViewFactory(**{'project': self.project})
        response = self.get(view, self.contributor)

        self.assertEquals(response.status_code, 403)

    def test_get_inactive_view_with_contributor(self):
        view = ViewFactory(**{
            'project': self.project,
            'status': 'deleted'
        })
        response = self.get(view, self.contributor)
        self.assertEquals(response.status_code, 404)

    def test_get_active_view_with_view_member(self):
        view = ViewFactory(**{'project': self.project})
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': view
        })
        response = self.get(view, self.view_member)

        self.assertEquals(response.status_code, 200)

    def test_get_inactive_view_with_view_member(self):
        view = ViewFactory(**{'project': self.project, 'status': 'deleted'})
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': view
        })
        response = self.get(view, self.view_member)
        self.assertEquals(response.status_code, 403)

    def test_get_active_view_with_non_member(self):
        view = ViewFactory(**{'project': self.project})
        response = self.get(view, self.some_dude)

        self.assertEquals(response.status_code, 403)

    def test_get_inactive_view_with_non_member(self):
        view = ViewFactory(**{
            'project': self.project,
            'status': 'deleted'
        })

        response = self.get(view, self.some_dude)
        self.assertEquals(response.status_code, 403)
