from django.test import TestCase

from nose.tools import raises

from rest_framework.test import APIRequestFactory, force_authenticate

from .model_factories import UserF, UserGroupF, ProjectF
from ..models import Project
from ..views import ProjectApiDetail


class ProjectAjaxTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })

    def test_unauthenticated(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'status': 'bockwurst'}
        )
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_update_with_wrong_status(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'status': 'bockwurst'}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 400)

    def test_update_project_status_with_admin(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'status': 'inactive'}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).status,
            'inactive'
        )

    def test_update_project_description_with_admin(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'description': 'new description'}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).description,
            'new description'
        )

    def test_update_project_description_with_contributor(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'description': 'new description'}
        )
        force_authenticate(request, user=self.contributor)
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).description,
            self.project.description
        )

    def test_update_project_description_with_non_member(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'description': 'new description'}
        )
        force_authenticate(request, user=self.non_member)
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).description,
            self.project.description
        )

    @raises(Project.DoesNotExist)
    def test_delete_project_with_admin(self):
        request = self.factory.delete('/api/projects/%s/' % self.project.id)
        force_authenticate(request, user=self.admin)
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 204)
        Project.objects.get(pk=self.project.id)

    def test_delete_project_with_contributor(self):
        request = self.factory.delete('/api/projects/%s/' % self.project.id)
        force_authenticate(request, user=self.contributor)
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).status,
            'active'
        )

    def test_delete_project_with_non_member(self):
        request = self.factory.delete('/api/projects/%s/' % self.project.id)
        force_authenticate(request, user=self.non_member)
        view = ProjectApiDetail.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).status,
            'active'
        )
