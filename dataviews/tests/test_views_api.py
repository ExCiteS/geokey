from django.test import TestCase
from django.core.urlresolvers import reverse

from core.tests.oauthfactories import AccessTokenFactory
from projects.tests.model_factories import UserF, ProjectF, UserGroupF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory


class TestDataViewsPublicAoi(TestCase):
    def test_get_active_view_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        token = AccessTokenFactory.create(**{
            'user': admin
        })
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin]),
        })
        view = ViewFactory(**{'project': project})

        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        response = self.client.get(
            url, **{'HTTP_AUTHORIZATION': 'Bearer ' + token.token})

        self.assertEquals(response.status_code, 200)

    def test_get_inactive_view_with_admin(self):
        admin = UserF.create(**{'password': '1'})
        token = AccessTokenFactory.create(**{
            'user': admin
        })
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        view = ViewFactory(**{
            'project': project,
            'status': 'deleted'
        })

        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        response = self.client.get(
            url, **{'HTTP_AUTHORIZATION': 'Bearer ' + token.token})
        self.assertEquals(response.status_code, 404)

    def test_get_active_view_with_contributor(self):
        user = UserF.create(**{'password': '1'})
        token = AccessTokenFactory.create(**{
            'user': user
        })
        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[user])
        })
        view = ViewFactory(**{'project': project})

        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        response = self.client.get(
            url, **{'HTTP_AUTHORIZATION': 'Bearer ' + token.token})

        self.assertEquals(response.status_code, 403)

    def test_get_inactive_view_with_contributor(self):
        user = UserF.create(**{'password': '1'})
        token = AccessTokenFactory.create(**{
            'user': user
        })
        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[user])
        })
        view = ViewFactory(**{
            'project': project,
            'status': 'deleted'
        })

        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        response = self.client.get(
            url, **{'HTTP_AUTHORIZATION': 'Bearer ' + token.token})
        self.assertEquals(response.status_code, 404)

    def test_get_active_view_with_view_member(self):
        user = UserF.create(**{'password': '1'})
        token = AccessTokenFactory.create(**{
            'user': user
        })
        project = ProjectF.create()
        view = ViewFactory(**{'project': project})
        ViewGroupFactory(add_users=[user], **{
            'view': view
        })

        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        response = self.client.get(
            url, **{'HTTP_AUTHORIZATION': 'Bearer ' + token.token})

        self.assertEquals(response.status_code, 200)

    def test_get_inactive_view_with_view_member(self):
        user = UserF.create(**{'password': '1'})
        token = AccessTokenFactory.create(**{
            'user': user
        })
        project = ProjectF.create()
        view = ViewFactory(**{'project': project, 'status': 'deleted'})
        ViewGroupFactory(add_users=[user], **{
            'view': view
        })

        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        response = self.client.get(
            url, **{'HTTP_AUTHORIZATION': 'Bearer ' + token.token})
        self.assertEquals(response.status_code, 403)

    def test_get_active_view_with_non_member(self):
        user = UserF.create(**{'password': '1'})
        token = AccessTokenFactory.create(**{
            'user': user
        })
        project = ProjectF.create()
        view = ViewFactory(**{'project': project})

        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        response = self.client.get(
            url, **{'HTTP_AUTHORIZATION': 'Bearer ' + token.token})

        self.assertEquals(response.status_code, 403)

    def test_get_inactive_view_with_non_member(self):
        user = UserF.create(**{'password': '1'})
        token = AccessTokenFactory.create(**{
            'user': user
        })
        project = ProjectF.create(**{
            'isprivate': False
        })
        view = ViewFactory(**{
            'project': project,
            'status': 'deleted'
        })

        url = reverse('api:single_view', kwargs={
            'project_id': view.project.id,
            'view_id': view.id
        })
        response = self.client.get(
            url, **{'HTTP_AUTHORIZATION': 'Bearer ' + token.token})
        self.assertEquals(response.status_code, 404)
