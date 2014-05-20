from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate

from .model_factories import UserF, ProjectF
from ..models import Project
from ..views import ProjectAdmins, ProjectAdminsUser


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
