from django.test import TestCase

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.views import projects_list

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
		private.admins.addUsers(zidane)
		private.contributors.addUsers(diego)
		private.save()

	def test_accessProjectsWithNonMember(self):
		mehmet = self._authenticate('mehmet')
		projects = projects_list(mehmet)
		self.assertEqual(len(projects), 1)
		for p in projects:
			self.assertNotIn(p.name, ('Private project', 'Inactive project'))

	def test_accessProjectWithCreator(self):
		eric = self._authenticate('eric')
		projects = projects_list(eric)
		self.assertEqual(len(projects), 3)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Inactive project', 'Private project'))

	def test_accessProjectInactiveWithAdmin(self):
		george = self._authenticate('george')
		projects = projects_list(george)
		self.assertEqual(len(projects), 2)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Inactive project'))

	def test_accessProjectPrivateWithAdmin(self):
		zidane = self._authenticate('zidane')
		projects = projects_list(zidane)
		self.assertEqual(len(projects), 2)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Private project'))

	def test_accessProjectPrivateWithContributer(self):
		diego = self._authenticate('diego')
		projects = projects_list(diego)
		self.assertEqual(len(projects), 2)
		for p in projects:
			self.assertIn(p.name, ('Public project', 'Private project'))