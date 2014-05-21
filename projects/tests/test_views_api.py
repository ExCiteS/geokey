import json

from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from rest_framework.test import APIRequestFactory, force_authenticate

from .model_factories import UserF, ProjectF
from ..views import Projects, SingleProject


class ProjectsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_member = UserF.create()

        self.public_project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member],
            **{
                'isprivate': False
            }
        )

        self.private_project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member]
        )

        self.inactive_project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member],
            **{
                'status': 'inactive'
            }
        )

        self.deleted_project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member],
            **{'isprivate': False}
        )
        self.deleted_project.delete()

    def test_get_projects_with_admin(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.admin)
        view = Projects.as_view()
        response = view(request).render()

        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 2)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_contributor(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.contributor)
        view = Projects.as_view()
        response = view(request).render()

        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 2)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_view_member(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.view_member)
        view = Projects.as_view()
        response = view(request).render()

        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 2)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_non_member(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.non_member)
        view = Projects.as_view()
        response = view(request).render()

        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 1)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)
        self.assertNotContains(response, self.private_project.name)

    def test_get_projects_with_anonymous(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=AnonymousUser())
        view = Projects.as_view()
        response = view(request).render()

        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 1)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)
        self.assertNotContains(response, self.private_project.name)


class SingleProjectTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_get_deleted_project_with_admin(self):
        user = UserF.create()

        project = ProjectF.create(
            add_admins=[user]
        )
        project.delete()

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_admin(self):
        user = UserF.create()

        project = ProjectF.create(
            add_admins=[user]
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_inactive_project_with_admin(self):
        user = UserF.create()

        project = ProjectF.create(
            add_admins=[user],
            **{'status': 'inactive'}
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_admin(self):
        user = UserF.create()

        project = ProjectF.create(
            add_admins=[user],
            **{'isprivate': False}
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_deleted_project_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(
            add_contributors=[user]
        )
        project.delete()

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(
            add_contributors=[user]
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_inactive_project_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(
            add_contributors=[user],
            **{'status': 'inactive'}
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(
            add_contributors=[user],
            **{'isprivate': False}
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_deleted_project_with_view_member(self):
        user = UserF.create()

        project = ProjectF.create(
            add_viewers=[user]
        )
        project.delete()

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_view_member(self):
        user = UserF.create()

        project = ProjectF.create(
            add_viewers=[user]
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": false')

    def test_get_inactive_project_with_view_member(self):
        user = UserF.create()

        project = ProjectF.create(
            add_viewers=[user],
            **{'status': 'inactive'}
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_view_member(self):
        user = UserF.create()

        project = ProjectF.create(
            add_viewers=[user],
            **{'isprivate': False}
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": false')

    def test_get_deleted_project_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create()
        project.delete()

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create()

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_get_inactive_project_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'status': 'inactive'
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'isprivate': False
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": false')

    def test_get_public_project_with_anonymous(self):
        user = AnonymousUser()

        project = ProjectF.create(**{
            'isprivate': False
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": false')
