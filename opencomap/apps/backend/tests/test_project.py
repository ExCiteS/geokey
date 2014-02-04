from base import Test

from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend import authorization as view

class ProjectViewTest(Test):
	class Meta: 
		app_label = 'backend'

	def test_access_projects_with_non_member(self):
		mehmet = self._authenticate('mehmet')
		projects = view.projects_list(mehmet)
		self.assertEqual(len(projects), 1)
		for p in projects:
			self.assertNotIn(p.name, ('Private project', 'Inactive project'))

	def test_access_projects_with_creator(self):
		eric = self._authenticate('eric')
		projects = view.projects_list(eric)
		self.assertEqual(len(projects), 3)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Inactive project', 'Private project'))

	def test_access_projects_with_admin(self):
		george = self._authenticate('george')
		projects = view.projects_list(george)
		self.assertEqual(len(projects), 3)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Inactive project', 'Private project'))

	def test_access_projects_with_contributor(self):
		diego = self._authenticate('diego')
		projects = view.projects_list(diego)
		self.assertEqual(len(projects), 2)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Private project'))

	def test_access_projects_with_viewgroup_member(self):
		carlos = self._authenticate('carlos')
		projects = view.projects_list(carlos)
		self.assertEqual(len(projects), 2)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Private project'))

	def test_access_single_project_with_non_member(self):
		mehmet = self._authenticate('mehmet')
		projects = Project.objects.all()
		for project in projects:
			if project.name == 'Public project':
				self.assertEqual(project, view.project(mehmet, project.id))
			if project.name == 'Inactive project':
				with self.assertRaises(PermissionDenied):
					view.project(mehmet, project.id)
			if project.name == 'Private project':
				with self.assertRaises(PermissionDenied):
					view.project(mehmet, project.id)
			if project.name == 'Deleted project':
				with self.assertRaises(Project.DoesNotExist):
					view.project(mehmet, project.id)

	def test_access_single_project_with_contributor(self):
		diego = self._authenticate('diego')
		projects = Project.objects.all()
		for project in projects:
			if project.name == 'Public project':
				self.assertEqual(project, view.project(diego, project.id))
			if project.name == 'Inactive project':
				with self.assertRaises(PermissionDenied):
					view.project(diego, project.id)
			if project.name == 'Private project':
				self.assertEqual(project, view.project(diego, project.id))
			if project.name == 'Deleted project':
				with self.assertRaises(Project.DoesNotExist):
					view.project(diego, project.id)

	def test_access_single_project_with_viewgroup_member(self):
		carlos = self._authenticate('carlos')
		projects = Project.objects.all()
		for project in projects:
			if project.name == 'Public project':
				self.assertEqual(project, view.project(carlos, project.id))
			if project.name == 'Inactive project':
				with self.assertRaises(PermissionDenied):
					view.project(carlos, project.id)
			if project.name == 'Private project':
				self.assertEqual(project, view.project(carlos, project.id))
			if project.name == 'Deleted project':
				with self.assertRaises(Project.DoesNotExist):
					view.project(carlos, project.id)

	def test_access_single_project_with_admins(self):
		george = self._authenticate('george')
		eric = self._authenticate('eric')
		projects = Project.objects.all()
		for project in projects:
			if project.name == 'Public project':
				self.assertEqual(project, view.project(george, project.id))
				self.assertEqual(project, view.project(eric, project.id))
			if project.name == 'Inactive project':
				self.assertEqual(project, view.project(george, project.id))
				self.assertEqual(project, view.project(eric, project.id))
			if project.name == 'Private project':
				self.assertEqual(project, view.project(george, project.id))
				self.assertEqual(project, view.project(eric, project.id))
			if project.name == 'Deleted project':
				with self.assertRaises(Project.DoesNotExist):
					view.project(george, project.id)
					view.project(eric, project.id)

	def test_update_single_project_with_admin(self):
		george = self._authenticate('george')
		eric = self._authenticate('eric')
		for project in Project.objects.all():
			if project.name == 'Private project':
				try:
					view.updateProject(george, project.id, {"description": "new description"})
				except PermissionDenied: 
					self.fail('updateProject() raised PermissionDenied unexpectedly')

				try:
					view.updateProject(eric, project.id, {"description": "new description"})
				except PermissionDenied: 
					self.fail('updateProject() raised PermissionDenied unexpectedly')

	def test_update_single_project_with_non_admin(self):
		diego = self._authenticate('diego')
		mehmet = self._authenticate('mehmet')
		carlos = self._authenticate('carlos')
		for project in Project.objects.all():
			with self.assertRaises(PermissionDenied):
				view.updateProject(diego, project.id, {"description": "new description"})
				view.updateProject(mehmet, project.id, {"description": "new description"})
				view.updateProject(carlos, project.id, {"description": "new description"})
			

