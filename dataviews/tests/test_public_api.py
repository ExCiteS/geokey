from django.test import TestCase
from django.core.urlresolvers import reverse

from provider.oauth2.models import AccessToken

from ..models import View


class TestAccessPermissions(TestCase):
    fixtures = ['fixtures.json', 'oauth.json']

    def _get_with_user(self, token, view):
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + token.token
        }
        url = reverse(
            'api:single_view',
            kwargs={
                'project_id': view.project_id,
                'view_id': view.id
            }
        )
        return self.client.get(url, **auth_headers)

    def test_get_view_of_public_project_with_admin(self):
        token = AccessToken.objects.get(user_id=1)
        view = View.objects.get(pk=1)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 200)

    def test_get_view_of_public_project_with_contributor(self):
        token = AccessToken.objects.get(user_id=2)
        view = View.objects.get(pk=1)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_public_project_with_deleted_view_member(self):
        token = AccessToken.objects.get(user_id=5)
        view = View.objects.get(pk=1)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_public_project_with_non_member(self):
        token = AccessToken.objects.get(user_id=4)
        view = View.objects.get(pk=1)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_private_project_with_admin(self):
        token = AccessToken.objects.get(user_id=1)
        view = View.objects.get(pk=2)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 200)

    def test_get_view_of_private_project_with_contributor(self):
        token = AccessToken.objects.get(user_id=2)
        view = View.objects.get(pk=2)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_private_project_with_deleted_view_member(self):
        token = AccessToken.objects.get(user_id=5)
        view = View.objects.get(pk=2)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_private_project_with_non_member(self):
        token = AccessToken.objects.get(user_id=4)
        view = View.objects.get(pk=2)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_inactive_project_with_admin(self):
        token = AccessToken.objects.get(user_id=1)
        view = View.objects.get(pk=3)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_inactive_project_with_contributor(self):
        token = AccessToken.objects.get(user_id=2)
        view = View.objects.get(pk=3)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_inactive_project_with_deleted_view_member(self):
        token = AccessToken.objects.get(user_id=5)
        view = View.objects.get(pk=3)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_inactive_project_with_non_member(self):
        token = AccessToken.objects.get(user_id=4)
        view = View.objects.get(pk=3)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 403)

    def test_get_view_of_deleted_project_with_admin(self):
        token = AccessToken.objects.get(user_id=1)
        view = View.objects.get(pk=4)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 404)

    def test_get_view_of_deleted_project_with_contributor(self):
        token = AccessToken.objects.get(user_id=2)
        view = View.objects.get(pk=4)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 404)

    def test_get_view_of_deleted_project_with_deleted_view_member(self):
        token = AccessToken.objects.get(user_id=5)
        view = View.objects.get(pk=4)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 404)

    def test_get_view_of_deleted_project_with_non_member(self):
        token = AccessToken.objects.get(user_id=4)
        view = View.objects.get(pk=4)
        response = self._get_with_user(token, view)
        self.assertEqual(response.status_code, 404)
