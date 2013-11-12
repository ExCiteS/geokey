from django.test import TestCase
from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.projects import ProjectFactory
from opencomap.apps.backend.models.permissions import UserGroup

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied


class ProjectTest(TestCase):
	class Meta: 
		app_label = 'backend'

	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def setUp(self):
		"""
		Inserts data into the database
		"""
		#Create Users
		userJohn = User.objects.create_user('john', 'lennon@thebeatles.com', 'john123')
		userJohn.save()
		userPaul = User.objects.create_user('paul', 'mccartney@thebeatles.com', 'paul123')
		userPaul.save()
		userRingo = User.objects.create_user('ringo', 'starr@thebeatles.com', 'ringo123')
		userRingo.save()
		userGeorge = User.objects.create_user('george', 'lennon@thebeatles.com', 'george123')
		userGeorge.save()

		
		john = self._authenticate('john')
		self.assertTrue((john is not None) and (john.is_active))

		paul = self._authenticate('paul')
		self.assertTrue((paul is not None) and (paul.is_active))

		ringo = self._authenticate('ringo')
		self.assertTrue((ringo is not None) and (ringo.is_active))

		george = self._authenticate('george')
		self.assertTrue((george is not None) and (george.is_active))
		
		# Create new projects
		project1 = ProjectFactory(name='Test 1', description='Test description for the project 1', creator=john)
		
		editGroup = UserGroup(name='Edit Group', can_view=True, can_contribute=True, can_edit=True)
		editGroup.save()
		editGroup.addUsers(ringo)

		contributeGroup = UserGroup(name='Edit Group', can_view=True, can_contribute=True)
		contributeGroup.save()
		contributeGroup.addUsers(george)

		project1.addUserGroups(editGroup, contributeGroup)
		# project2 = projects.createProject(name='Test 2', description='Test description for the project 2', creator=paul)
		# project3 = projects.createProject(name='Test 3', description='Test description for the project 3', creator=ringo)
		# project4 = projects.createProject(name='Test 4', description='Test description for the project 4', creator=george)

	def test_general_rights(self):
		"""
		Tests that 1 + 1 always equals 2.
		"""
		john = self._authenticate('john')
		self.assertTrue((john is not None) and (john.is_active))

		paul = self._authenticate('paul')
		self.assertTrue((paul is not None) and (paul.is_active))

		ringo = self._authenticate('ringo')
		self.assertTrue((ringo is not None) and (ringo.is_active))

		george = self._authenticate('george')
		self.assertTrue((george is not None) and (george.is_active))

		for project in Project.objects.all():
			if project.name == 'Test 1':
				self.assertTrue(project.userCanView(john))
				self.assertTrue(project.userCanView(paul))
				self.assertTrue(project.userCanView(ringo))
				self.assertTrue(project.userCanView(george))

				self.assertTrue(project.userCanContribute(john))
				self.assertTrue(project.userCanContribute(george))
				self.assertTrue(project.userCanContribute(ringo))
				self.assertFalse(project.userCanContribute(paul))

				self.assertTrue(project.userCanEdit(john))
				self.assertTrue(project.userCanEdit(ringo))
				self.assertFalse(project.userCanEdit(paul))
				self.assertFalse(project.userCanEdit(george))

				self.assertTrue(project.userCanAdmin(john))
				self.assertFalse(project.userCanAdmin(paul))
				self.assertFalse(project.userCanAdmin(ringo))
				self.assertFalse(project.userCanAdmin(george))

	def test_project_update(self):
		project = Project.objects.filter(name='Test 1')[0]
		
		john = self._authenticate('john')
		self.assertTrue((john is not None) and (john.is_active))

		george = self._authenticate('george')
		self.assertTrue((george is not None) and (george.is_active))

		result = project.update(john, name='Johns project', description='Johns project description')
		self.assertEqual(result.name, 'Johns project')
		self.assertEqual(result.description, 'Johns project description')

		with self.assertRaises(PermissionDenied):
			project.update(george, name='Goerges project', description='Georges project description')


	def test_project_delete(self):
		project = Project.objects.filter(name='Test 1')[0]
		
		john = self._authenticate('john')
		self.assertTrue((john is not None) and (john.is_active))

		george = self._authenticate('george')
		self.assertTrue((george is not None) and (george.is_active))

		with self.assertRaises(PermissionDenied):
			project.remove(george)

		self.assertTrue(project.remove(john))
		