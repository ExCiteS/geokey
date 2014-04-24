import json

from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate

from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory

from .model_factories import UserF, UserGroupF, ProjectF
from ..views import ProjectApiList, ProjectApiSingle


class ProjectApiListTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_member = UserF.create()

        self.public_project = ProjectF.create(**{
            'isprivate': False,
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.public_project
            })
        })

        self.private_project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.private_project
            })
        })

        self.inactive_project = ProjectF.create(**{
            'status': 'inactive',
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.inactive_project
            })
        })

        self.deleted_project = ProjectF.create(**{
            'status': 'deleted',
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor])
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.deleted_project
            })
        })

        self.private_everyone_project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
            'everyonecontributes': True
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.private_everyone_project
            })
        })

        self.public_everyone_project = ProjectF.create(**{
            'isprivate': False,
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
            'everyonecontributes': True
        })
        ViewGroupFactory(add_users=[self.view_member], **{
            'view': ViewFactory(**{
                'project': self.public_everyone_project
            })
        })

    def test_get_projects_with_admin(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.admin)
        view = ProjectApiList.as_view()
        response = view(request).render()

        projects = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 4)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_contributor(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.contributor)
        view = ProjectApiList.as_view()
        response = view(request).render()

        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 4)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_view_member(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.view_member)
        view = ProjectApiList.as_view()
        response = view(request).render()

        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 4)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)

    def test_get_projects_with_non_member(self):
        request = self.factory.get('/api/projects/')
        force_authenticate(request, user=self.non_member)
        view = ProjectApiList.as_view()
        response = view(request).render()

        projects = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 2)
        self.assertNotContains(response, self.inactive_project.name)
        self.assertNotContains(response, self.deleted_project.name)
        self.assertNotContains(response, self.private_project.name)


class ProjectApiSingleTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_get_deleted_project_with_admin(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'status': 'deleted',
            'admins': UserGroupF(add_users=[user])
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_admin(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[user])
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_inactive_project_with_admin(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'status': 'inactive',
            'admins': UserGroupF(add_users=[user])
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_admin(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'isprivate': False,
            'admins': UserGroupF(add_users=[user])
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_deleted_project_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'status': 'deleted',
            'contributors': UserGroupF(add_users=[user])
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[user])
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_inactive_project_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'status': 'inactive',
            'contributors': UserGroupF(add_users=[user])
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[user])
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')

    def test_get_deleted_project_with_view_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'status': 'deleted'
        })
        ViewGroupFactory(add_users=[user], **{
            'view': ViewFactory(**{
                'project': project
            })
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_view_member(self):
        user = UserF.create()

        project = ProjectF.create()
        ViewGroupFactory(add_users=[user], **{
            'view': ViewFactory(**{
                'project': project
            })
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": false')

    def test_get_inactive_project_with_view_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'status': 'inactive'
        })
        ViewGroupFactory(add_users=[user], **{
            'view': ViewFactory(**{
                'project': project
            })
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_get_public_project_with_view_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'isprivate': False
        })
        ViewGroupFactory(add_users=[user], **{
            'view': ViewFactory(**{
                'project': project
            })
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": false')

    def test_get_deleted_project_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'status': 'deleted'
        })

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 404)

    def test_get_private_project_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create()

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = ProjectApiSingle.as_view()
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
        view = ProjectApiSingle.as_view()
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
        view = ProjectApiSingle.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": false')
