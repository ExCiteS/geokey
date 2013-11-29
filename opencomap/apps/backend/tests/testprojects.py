from django.test import TestCase
from opencomap.apps.backend.models.factory import Factory
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.choice import STATUS_TYPES

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class ProjectTest(TestCase):
	class Meta: 
		app_label = 'backend'

	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def setUp(self):
		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('zidane', 'zinedine@zidane.fr', 'zinedine123', first_name='Zinedine', last_name='Zidane').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diegoe123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('carlos', 'carlos@valderama.co', 'carlos123', first_name='Carlos', last_name='Valderama').save()

	def test_projectPermissions(self):
		admin = self._authenticate('eric')
		user = self._authenticate('george')
		project1 = Factory().createProject('Test Project', 'Test description', admin)

		self.assertTrue(project1.userCanAdmin(admin))
		self.assertTrue(project1.userCanEdit(admin))
		self.assertTrue(project1.userCanContribute(admin))
		self.assertTrue(project1.userCanView(admin))

		self.assertFalse(project1.userCanAdmin(user))
		self.assertFalse(project1.userCanEdit(user))
		self.assertFalse(project1.userCanContribute(user))
		self.assertTrue(project1.userCanView(user))
		
	def test_deleteProject(self):
		admin = self._authenticate('eric')
		project1 = Factory().createProject('Test Project', 'Test description', admin)

		project1.delete()
		self.assertEqual(project1.status, STATUS_TYPES['DELETED'])

	def test_updateProject(self):
		admin = self._authenticate('eric')

		project1 = Factory().createProject('Test Project', 'Test description', admin)

		project1.update(name='Updated name')
		self.assertEqual(project1.name, 'Updated name')

		project1.update(description='Updated description')
		self.assertEqual(project1.description, 'Updated description')

		project1.update(name='Another Updated name', description='Another Updated description')
		self.assertEqual(project1.name, 'Another Updated name')
		self.assertEqual(project1.description, 'Another Updated description')


	def test_createProject(self):
		admin = self._authenticate('eric')

		project1 = Factory().createProject('Test Project', 'Test description', admin)
		self.assertEqual(len(Project.objects.all()), 1)
		self.assertEqual(Project.objects.all()[0], project1)

		usergroups = project1.getUserGroups()
		self.assertEqual(len(usergroups), 2)
		for group in usergroups:
			if (group.is_admin):
				self.assertTrue(group.can_admin)
				self.assertTrue(group.can_edit)
				self.assertTrue(group.can_contribute)
				self.assertTrue(group.can_view)

			if (group.is_everyone):
				self.assertFalse(group.can_admin)
				self.assertFalse(group.can_edit)
				self.assertFalse(group.can_contribute)
				self.assertTrue(group.can_view)

		self.assertTrue(project1.userCanAdmin(admin))