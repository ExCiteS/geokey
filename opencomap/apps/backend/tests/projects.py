from django.test import TestCase
from opencomap.apps.backend.models.factory import Factory
from opencomap.apps.backend.models.projects import Project

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied

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

		with self.assertRaises(PermissionDenied):
			project1.update(user, name='Updated name')
			project1.remove(user)

		project1.update(admin, name='Updated name')
		project1.remove(admin)



	def test_deleteProject(self):
		admin = self._authenticate('eric')
		project1 = Factory().createProject('Test Project', 'Test description', admin)

		project1.remove(admin)
		self.assertEqual(project1.status, 4)

	def test_updateProject(self):
		admin = self._authenticate('eric')

		project1 = Factory().createProject('Test Project', 'Test description', admin)

		project1.update(admin, name='Updated name')
		self.assertEqual(project1.name, 'Updated name')

		project1.update(admin, description='Updated description')
		self.assertEqual(project1.description, 'Updated description')

		project1.update(admin, name='Another Updated name', description='Another Updated description')
		self.assertEqual(project1.name, 'Another Updated name')
		self.assertEqual(project1.description, 'Another Updated description')


	def test_createProject(self):
		admin = self._authenticate('eric')

		project1 = Factory().createProject('Test Project', 'Test description', admin)
		self.assertEqual(len(Project.objects.all()), 1)
		self.assertEqual(Project.objects.all()[0], project1)

		usergroups = project1.getUserGroups(admin)
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





	# def test_general_rights(self):
	# 	"""
	# 	Tests that 1 + 1 always equals 2.
	# 	"""
	# 	john = self._authenticate('john')
	# 	self.assertTrue((john is not None) and (john.is_active))

	# 	paul = self._authenticate('paul')
	# 	self.assertTrue((paul is not None) and (paul.is_active))

	# 	ringo = self._authenticate('ringo')
	# 	self.assertTrue((ringo is not None) and (ringo.is_active))

	# 	george = self._authenticate('george')
	# 	self.assertTrue((george is not None) and (george.is_active))

	# 	for project in Project.objects.all():
	# 		if project.name == 'Test 1':
	# 			self.assertTrue(project.userCanView(john))
	# 			self.assertTrue(project.userCanView(paul))
	# 			self.assertTrue(project.userCanView(ringo))
	# 			self.assertTrue(project.userCanView(george))

	# 			self.assertTrue(project.userCanContribute(john))
	# 			self.assertTrue(project.userCanContribute(george))
	# 			self.assertTrue(project.userCanContribute(ringo))
	# 			self.assertFalse(project.userCanContribute(paul))

	# 			self.assertTrue(project.userCanEdit(john))
	# 			self.assertTrue(project.userCanEdit(ringo))
	# 			self.assertFalse(project.userCanEdit(paul))
	# 			self.assertFalse(project.userCanEdit(george))

	# 			self.assertTrue(project.userCanAdmin(john))
	# 			self.assertFalse(project.userCanAdmin(paul))
	# 			self.assertFalse(project.userCanAdmin(ringo))
	# 			self.assertFalse(project.userCanAdmin(george))

	# def test_project_update(self):
	# 	project = Project.objects.filter(name='Test 1')[0]
		
	# 	john = self._authenticate('john')
	# 	self.assertTrue((john is not None) and (john.is_active))

	# 	george = self._authenticate('george')
	# 	self.assertTrue((george is not None) and (george.is_active))

	# 	project.update(john, name='Johns project', description='Johns project description')
	# 	self.assertEqual(project.name, 'Johns project')
	# 	self.assertEqual(project.description, 'Johns project description')


	# def test_project_delete(self):
	# 	project = Project.objects.filter(name='Test 1')[0]
		
	# 	john = self._authenticate('john')
		
	# 	project.remove(john)
	# 	self.assertEqual(project.status, 4)

	# def test_usergroup_mgmt(self):
	# 	project = Project.objects.filter(name='Test 1')[0]
		
	# 	john = self._authenticate('john')
	# 	ringo = self._authenticate('ringo')
	# 	george = self._authenticate('george')

	# 	testGroup = UserGroup(name='Test Group', can_view=True, can_contribute=True, can_edit=True)
	# 	testGroup.save()
	# 	testGroup.addUsers(ringo)

	# 	project.addUserGroups(john, testGroup)
	# 	groups = project.usergroups.all()
	# 	self.assertEqual(len(groups), 5)

	# 	removeGroup = project.usergroups.filter(name='Test Group')[0]
	# 	project.removeUserGroups(john, removeGroup)
	# 	groups = project.usergroups.all()
	# 	self.assertEqual(len(groups), 4)

	# 	for group in groups:
	# 		self.assertFalse(group.name == 'Test Group')