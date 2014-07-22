import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from nose.tools import raises

from rest_framework.test import APIRequestFactory, force_authenticate

from dataviews.tests.model_factories import ViewFactory

from .model_factories import UserF, ProjectF
from ..models import Project
from ..views import (
    ProjectCreate, ProjectSettings, ProjectUpdate, ProjectAdmins,
    ProjectAdminsUser, Projects, SingleProject, ProjectOverview
)

# ############################################################################
#
# ADMIN VIEWS
#
# ############################################################################


class ProjectCreateTest(TestCase):
    def test_get_with_user(self):
        view = ProjectCreate.as_view()
        url = reverse('admin:project_create')
        request = APIRequestFactory().get(url)
        request.user = UserF.create()
        response = view(request).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_anonymous(self):
        view = ProjectCreate.as_view()
        url = reverse('admin:project_create')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))


class ProjectSettingsTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.view_member = UserF.create()
        self.contributor = UserF.create()
        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member],
            **{
                'creator': self.creator
            }
        )

    def test_get_with_creator(self):
        view = ProjectSettings.as_view()
        url = reverse('admin:project_settings',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.creator
        response = view(request, project_id=self.project.id).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_admin(self):
        view = ProjectSettings.as_view()
        url = reverse('admin:project_settings',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.admin
        response = view(request, project_id=self.project.id).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_contributor(self):
        view = ProjectSettings.as_view()
        url = reverse('admin:project_settings',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.contributor
        response = view(request, project_id=self.project.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_with_view_member(self):
        view = ProjectSettings.as_view()
        url = reverse('admin:project_settings',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.view_member
        response = view(request, project_id=self.project.id)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_with_anonymous(self):
        view = ProjectSettings.as_view()
        url = reverse('admin:project_create')
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_deleted_project(self):
        self.project.delete()
        view = ProjectSettings.as_view()
        url = reverse('admin:project_settings',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.admin
        response = view(request, project_id=self.project.id).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Project matching query does not exist.')


class ProjectOverviewTest(TestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.view_member = UserF.create()
        self.contributor = UserF.create()
        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member],
            **{
                'creator': self.creator
            }
        )

    def test_get_with_admin(self):
        view = ProjectOverview.as_view()
        url = reverse('admin:project_overview',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.admin
        response = view(request, project_id=self.project.id).render()
        self.assertEqual(response.status_code, 200)

    def test_get_with_contributor(self):
        view = ProjectOverview.as_view()
        url = reverse('admin:project_overview',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.contributor
        response = view(request, project_id=self.project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_with_view_member(self):
        view = ProjectOverview.as_view()
        url = reverse('admin:project_overview',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.view_member
        response = view(request, project_id=self.project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_with_anonymous(self):
        view = ProjectOverview.as_view()
        url = reverse('admin:project_overview',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = AnonymousUser()
        response = view(request)
        self.assertTrue(isinstance(response, HttpResponseRedirect))

    def test_get_deleted_project(self):
        self.project.delete()
        view = ProjectOverview.as_view()
        url = reverse('admin:project_overview',
                      kwargs={'project_id': self.project.id})
        request = APIRequestFactory().get(url)
        request.user = self.admin
        response = view(request, project_id=self.project.id).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Project matching query does not exist.')


# ############################################################################
#
# AJAX VIEWS
#
# ############################################################################

class ProjectUpdateTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

    def test_unauthenticated(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'status': 'bockwurst'}
        )
        view = ProjectUpdate.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 403)

    def test_update_with_wrong_status(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'status': 'bockwurst'}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectUpdate.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 400)

    def test_update_project_status_with_admin(self):
        request = self.factory.put(
            '/api/projects/%s/' % self.project.id,
            {'status': 'inactive'}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectUpdate.as_view()
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
        view = ProjectUpdate.as_view()
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
        view = ProjectUpdate.as_view()
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
        view = ProjectUpdate.as_view()
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
        view = ProjectUpdate.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 204)
        Project.objects.get(pk=self.project.id)

    def test_delete_project_with_contributor(self):
        request = self.factory.delete('/api/projects/%s/' % self.project.id)
        force_authenticate(request, user=self.contributor)
        view = ProjectUpdate.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).status,
            'active'
        )

    def test_delete_project_with_non_member(self):
        request = self.factory.delete('/api/projects/%s/' % self.project.id)
        force_authenticate(request, user=self.non_member)
        view = ProjectUpdate.as_view()
        response = view(request, project_id=self.project.id).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Project.objects.get(pk=self.project.id).status,
            'active'
        )


class ProjectAdminsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.user_to_add = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

    def test_add_not_existing_user(self):
        request = self.factory.post(
            '/ajax/projects/%s/admins/' % (self.project.id) + '/',
            {'userId': 468476351545643131}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectAdmins.as_view()
        response = view(
            request,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 400)

    def test_add_admin_with_admin(self):
        request = self.factory.post(
            '/ajax/projects/%s/admins/' % (self.project.id) + '/',
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.admin)
        view = ProjectAdmins.as_view()
        response = view(
            request,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            self.user_to_add,
            Project.objects.get(pk=self.project.id).admins.all()
        )

    def test_add_admin_with_contributor(self):
        request = self.factory.post(
            '/ajax/projects/%s/admins/' % (self.project.id) + '/',
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.contributor)
        view = ProjectAdmins.as_view()
        response = view(
            request,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(pk=self.project.id).admins.all()
        )

    def test_add_admin_with_non_member(self):
        request = self.factory.post(
            '/ajax/projects/%s/admins/' % (self.project.id) + '/',
            {'userId': self.user_to_add.id}
        )
        force_authenticate(request, user=self.non_member)
        view = ProjectAdmins.as_view()
        response = view(
            request,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(
            self.user_to_add,
            Project.objects.get(pk=self.project.id).admins.all()
        )


class ProjectAdminsUserTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.admin_to_remove = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin, self.admin_to_remove],
            add_contributors=[self.contributor]
        )

    def test_delete_not_existing_admin(self):
        user = UserF.create()
        request = self.factory.delete(
            '/ajax/projects/%s/admins/%s/' %
            (self.project.id, user.id)
        )
        force_authenticate(request, user=self.admin)
        view = ProjectAdminsUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            user_id=user.id
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_delete_adminuser_with_admin(self):
        request = self.factory.delete(
            '/ajax/projects/%s/admins/%s/' %
            (self.project.id, self.admin_to_remove.id)
        )
        force_authenticate(request, user=self.admin)
        view = ProjectAdminsUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            user_id=self.admin_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertNotIn(
            self.admin_to_remove,
            Project.objects.get(pk=self.project.id).admins.all()
        )

    def test_delete_adminuser_with_contributor(self):
        request = self.factory.delete(
            '/ajax/projects/%s/admins/%s/' %
            (self.project.id, self.admin_to_remove.id)
        )
        force_authenticate(request, user=self.contributor)
        view = ProjectAdminsUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            user_id=self.admin_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.admin_to_remove,
            Project.objects.get(pk=self.project.id).admins.all()
        )

    def test_delete_adminuser_with_non_member(self):
        request = self.factory.delete(
            '/ajax/projects/%s/admins/%s/' %
            (self.project.id, self.admin_to_remove.id)
        )
        force_authenticate(request, user=self.non_member)
        view = ProjectAdminsUser.as_view()
        response = view(
            request,
            project_id=self.project.id,
            user_id=self.admin_to_remove.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            self.admin_to_remove,
            Project.objects.get(pk=self.project.id).admins.all()
        )


# ############################################################################
#
# API VIEWS
#
# ############################################################################

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
            **{
                'isprivate': False
            }
        )

        ViewFactory(
            add_viewers=[self.view_member],
            **{'project': self.public_project, 'isprivate': False}
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
            add_admins=[user],
            add_viewers=[UserF.create()]
        )

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": true')
        self.assertContains(response, '"is_involved": true')
        self.assertContains(response, '"num_contributions"')

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
        ViewFactory(**{'project': project, 'isprivate': False})

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
        ViewFactory(**{'project': project, 'isprivate': False})

        request = self.factory.get(
            '/api/projects/%s/' % project.id)
        force_authenticate(request, user=user)
        view = SingleProject.as_view()
        response = view(request, project_id=project.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.name)
        self.assertContains(response, '"can_contribute": false')
