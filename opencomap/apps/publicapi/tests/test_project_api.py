from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.choice import STATUS_TYPES

from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import json
from opencomap.apps.backend.serializers import SingleSerializer
from opencomap.apps.backend.serializers import ObjectSerializer

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.choice import STATUS_TYPES

class ProjectApiTest(TestCase):
	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def setUp(self):
		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diego123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('carlos', 'carlos@valderama.de', 'carlos123', first_name='carlos', last_name='valderama').save()

		eric = self._authenticate('eric')
		george = self._authenticate('george')
		diego = self._authenticate('diego')
		carlos = self._authenticate('carlos')

		self.privateproject = Factory.createProject('Private Project', 'Test description', eric, isprivate=True)
		self.privateproject.admins.addUsers(george)
		self.privateproject.contributors.addUsers(diego)
		self.privateproject.save()

		self.publicproject = Factory.createProject('Public Project', 'Test description', eric)

		self.inactiveproject = Factory.createProject('Inactive Project', 'Test description', eric)
		self.inactiveproject.admins.addUsers(george)
		self.inactiveproject.contributors.addUsers(diego)
		self.inactiveproject.update(status=STATUS_TYPES['INACTIVE'])

		self.deletedproject = Factory.createProject('Deleted Project', 'Test description', eric)
		self.deletedproject.delete()

		self.client = Client()
		self.singleSerializer = SingleSerializer()
		self.objectSerializer = ObjectSerializer()

	def test_projectsListWithCreator(self):
		self.client.login(username='eric', password='eric123')
		response = self.client.get('/api/projects', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithAdmin(self):
		self.client.login(username='george', password='george123')
		response = self.client.get('/api/projects', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithContributor(self):
		self.client.login(username='diego', password='diego123')
		response = self.client.get('/api/projects', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithNonMember(self):
		self.client.login(username='mehmet', password='mehmet123')
		response = self.client.get('/api/projects', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.privateproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_singleProjectsWithCreator(self):
		self.client.login(username='eric', password='eric123')

		response = self.client.get('/api/projects/' + str(self.publicproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))

		response = self.client.get('/api/projects/' + str(self.privateproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))

		response = self.client.get('/api/projects/' + str(self.inactiveproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveproject))

		response = self.client.get('/api/projects/' + str(self.deletedproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 404)
		
	def test_singleProjectsWithAdmin(self):
		self.client.login(username='george', password='george123')

		response = self.client.get('/api/projects/' + str(self.publicproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))

		response = self.client.get('/api/projects/' + str(self.privateproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))

		response = self.client.get('/api/projects/' + str(self.inactiveproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveproject))

		response = self.client.get('/api/projects/' + str(self.deletedproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 404)


	def test_singleProjectsWithContributor(self):
		self.client.login(username='diego', password='diego123')

		response = self.client.get('/api/projects/' + str(self.publicproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))

		response = self.client.get('/api/projects/' + str(self.privateproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))

		response = self.client.get('/api/projects/' + str(self.inactiveproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 401)

		response = self.client.get('/api/projects/' + str(self.deletedproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 404)

	def test_singleProjectsWithNonMember(self):
		self.client.login(username='mehmet', password='mehmet123')

		response = self.client.get('/api/projects/' + str(self.publicproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))

		response = self.client.get('/api/projects/' + str(self.privateproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 401)

		response = self.client.get('/api/projects/' + str(self.inactiveproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 401)

		response = self.client.get('/api/projects/' + str(self.deletedproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 404)
