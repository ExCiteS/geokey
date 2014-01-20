from django.test import TestCase

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend import authorization as view

class ProjectViewTest(TestCase):
	class Meta: 
		app_label = 'backend'

	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def setUp(self):
		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('zidane', 'zinedine@zidane.fr', 'zidane123', first_name='Zinedine', last_name='Zidane').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diego123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('carlos', 'carlos@valderama.co', 'carlos123', first_name='Carlos', last_name='Valderama').save()

		eric = self._authenticate('eric')
		george = self._authenticate('george')
		mehmet = self._authenticate('mehmet')
		zidane = self._authenticate('zidane')
		diego = self._authenticate('diego')

		public = Factory.createProject('Public project', 'Test description', eric)
		public.save()

		inactive = Factory.createProject('Inactive project', 'Test description', eric)
		inactive.status = STATUS_TYPES['INACTIVE']
		inactive.admins.addUsers(george)
		inactive.save()

		private = Factory.createProject('Private project', 'Test description', eric, isprivate=True)
		private.admins.addUsers(george)
		private.contributors.addUsers(diego)
		private.save()

		deleted = Factory.createProject('Deleted project', 'Test description', eric)
		deleted.delete()
		deleted.save()

	def test_accessProjectsWithNonMember(self):
		mehmet = self._authenticate('mehmet')
		projects = view.projects_list(mehmet)
		self.assertEqual(len(projects), 1)
		for p in projects:
			self.assertNotIn(p.name, ('Private project', 'Inactive project'))

	def test_accessProjectsWithCreator(self):
		eric = self._authenticate('eric')
		projects = view.projects_list(eric)
		self.assertEqual(len(projects), 3)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Inactive project', 'Private project'))

	def test_accessProjectsInactiveWithAdmin(self):
		george = self._authenticate('george')
		projects = view.projects_list(george)
		self.assertEqual(len(projects), 3)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Inactive project', 'Private project'))

	def test_accessProjectsPrivateWithContributor(self):
		diego = self._authenticate('diego')
		projects = view.projects_list(diego)
		self.assertEqual(len(projects), 2)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Private project'))

	def test_accessProjectWithNonMenber(self):
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
				with self.assertRaises(ObjectDoesNotExist):
					view.project(mehmet, project.id)

	def test_accessProjectWithContributor(self):
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
				with self.assertRaises(ObjectDoesNotExist):
					view.project(diego, project.id)

	def test_accessProjectWithAdmins(self):
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

	def testUpdateProjectWithAdmin(self):
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

	def testUpdateProjectWithNonAdmin(self):
		diego = self._authenticate('diego')
		mehmet = self._authenticate('mehmet')
		for project in Project.objects.all():
			with self.assertRaises(PermissionDenied):
				view.updateProject(diego, project.id, {"description": "new description"})
				view.updateProject(mehmet, project.id, {"description": "new description"})
			





