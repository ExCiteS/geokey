from opencomap.tests.base import CommunityMapsTest
from django.core.exceptions import PermissionDenied

from backend.models import Project
from backend import authorization


class ProjectAuthorizationTest(CommunityMapsTest):
    class Meta: 
        app_label = 'backend'

    def test_access_projects_with_non_member(self):
        mehmet = self._authenticate('mehmet')
        projects = authorization.projects.get_list(mehmet)
        self.assertEqual(len(projects), 1)
        for p in projects:
            self.assertNotIn(p.name, ('Private project', 'Inactive project'))

    def test_access_projects_with_creator(self):
        eric = self._authenticate('eric')
        projects = authorization.projects.get_list(eric)
        self.assertEqual(len(projects), 3)
        for p in projects:
            self.assertIn(p.name, ('Public project', 'Inactive project', 'Private project'))

    def test_access_projects_with_admin(self):
        george = self._authenticate('george')
        projects = authorization.projects.get_list(george)
        self.assertEqual(len(projects), 3)
        for p in projects:
            self.assertIn(p.name, ('Public project', 'Inactive project', 'Private project'))

    def test_access_projects_with_contributor(self):
        diego = self._authenticate('diego')
        projects = authorization.projects.get_list(diego)
        self.assertEqual(len(projects), 2)
        for p in projects:
            self.assertIn(p.name, ('Public project', 'Private project'))

    def test_access_projects_with_viewgroup_member(self):
        carlos = self._authenticate('carlos')
        projects = authorization.projects.get_list(carlos)
        self.assertEqual(len(projects), 2)
        for p in projects:
            self.assertIn(p.name, ('Public project', 'Private project'))

        luis = self._authenticate('luis')
        projects = authorization.projects.get_list(luis)
        self.assertEqual(len(projects), 2)
        for p in projects:
            self.assertIn(p.name, ('Public project', 'Private project'))

    def test_access_projects_with_deleted_viewgroup_member(self):
        zidane = self._authenticate('zidane')
        projects = authorization.projects.get_list(zidane)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, 'Public project')

    def test_access_single_project_with_non_member(self):
        mehmet = self._authenticate('mehmet')
        projects = Project.objects.all()
        for project in projects:
            if project.name == 'Public project':
                self.assertEqual(project, authorization.projects.get_single(mehmet, project.id))
            if project.name == 'Inactive project':
                with self.assertRaises(PermissionDenied):
                    authorization.projects.get_single(mehmet, project.id)
            if project.name == 'Private project':
                with self.assertRaises(PermissionDenied):
                    authorization.projects.get_single(mehmet, project.id)
            if project.name == 'Deleted project':
                with self.assertRaises(Project.DoesNotExist):
                    authorization.projects.get_single(mehmet, project.id)

    def test_access_single_project_with_contributor(self):
        diego = self._authenticate('diego')
        projects = Project.objects.all()
        for project in projects:
            if project.name == 'Public project':
                self.assertEqual(project, authorization.projects.get_single(diego, project.id))
            if project.name == 'Inactive project':
                with self.assertRaises(PermissionDenied):
                    authorization.projects.get_single(diego, project.id)
            if project.name == 'Private project':
                self.assertEqual(project, authorization.projects.get_single(diego, project.id))
            if project.name == 'Deleted project':
                with self.assertRaises(Project.DoesNotExist):
                    authorization.projects.get_single(diego, project.id)

    def test_access_single_project_with_viewgroup_member(self):
        carlos = self._authenticate('carlos')
        projects = Project.objects.all()
        for project in projects:
            if project.name == 'Public project':
                self.assertEqual(project, authorization.projects.get_single(carlos, project.id))
            if project.name == 'Inactive project':
                with self.assertRaises(PermissionDenied):
                    authorization.projects.get_single(carlos, project.id)
            if project.name == 'Private project':
                self.assertEqual(project, authorization.projects.get_single(carlos, project.id))
            if project.name == 'Deleted project':
                with self.assertRaises(Project.DoesNotExist):
                    authorization.projects.get_single(carlos, project.id)

        luis = self._authenticate('luis')
        projects = Project.objects.all()
        for project in projects:
            if project.name == 'Public project':
                self.assertEqual(project, authorization.projects.get_single(luis, project.id))
            if project.name == 'Inactive project':
                with self.assertRaises(PermissionDenied):
                    authorization.projects.get_single(luis, project.id)
            if project.name == 'Private project':
                self.assertEqual(project, authorization.projects.get_single(luis, project.id))
            if project.name == 'Deleted project':
                with self.assertRaises(Project.DoesNotExist):
                    authorization.projects.get_single(luis, project.id)

    def test_access_single_project_with_deleted_viewgroup_member(self):
        zidane = self._authenticate('zidane')
        projects = Project.objects.all()
        for project in projects:
            if project.name == 'Public project':
                self.assertEqual(project, authorization.projects.get_single(zidane, project.id))
            if project.name == 'Inactive project':
                with self.assertRaises(PermissionDenied):
                    authorization.projects.get_single(zidane, project.id)
            if project.name == 'Private project':
                with self.assertRaises(PermissionDenied):
                    authorization.projects.get_single(zidane, project.id)
            if project.name == 'Deleted project':
                with self.assertRaises(Project.DoesNotExist):
                    authorization.projects.get_single(zidane, project.id)

    def test_access_single_project_with_admins(self):
        george = self._authenticate('george')
        eric = self._authenticate('eric')
        projects = Project.objects.all()
        for project in projects:
            if project.name == 'Public project':
                self.assertEqual(project, authorization.projects.get_single(george, project.id))
                self.assertEqual(project, authorization.projects.get_single(eric, project.id))
            if project.name == 'Inactive project':
                self.assertEqual(project, authorization.projects.get_single(george, project.id))
                self.assertEqual(project, authorization.projects.get_single(eric, project.id))
            if project.name == 'Private project':
                self.assertEqual(project, authorization.projects.get_single(george, project.id))
                self.assertEqual(project, authorization.projects.get_single(eric, project.id))
            if project.name == 'Deleted project':
                with self.assertRaises(Project.DoesNotExist):
                    authorization.projects.get_single(george, project.id)
                    authorization.projects.get_single(eric, project.id)

    def test_update_single_project_with_admin(self):
        george = self._authenticate('george')
        eric = self._authenticate('eric')
        for project in Project.objects.all():
            if project.name == 'Private project':
                try:
                    authorization.projects.update(george, project.id, {"description": "new description"})
                except PermissionDenied: 
                    self.fail('updateProject() raised PermissionDenied unexpectedly')

                try:
                    authorization.projects.update(eric, project.id, {"description": "new description"})
                except PermissionDenied: 
                    self.fail('updateProject() raised PermissionDenied unexpectedly')

    def test_update_single_project_with_non_admin(self):
        diego = self._authenticate('diego')
        mehmet = self._authenticate('mehmet')
        carlos = self._authenticate('carlos')
        luis = self._authenticate('luis')
        for project in Project.objects.all():
            with self.assertRaises(PermissionDenied):
                authorization.projects.update(diego, project.id, {"description": "new description"})
                authorization.projects.update(mehmet, project.id, {"description": "new description"})
                authorization.projects.update(carlos, project.id, {"description": "new description"})
                authorization.projects.update(luis, project.id, {"description": "new description"})
            

