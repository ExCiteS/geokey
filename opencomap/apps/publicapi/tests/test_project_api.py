from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from provider.oauth2.models import Client as OAuthClient

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.choice import STATUS_TYPES

import json
from opencomap.libs.serializers import SingleSerializer, ObjectSerializer

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.choice import STATUS_TYPES

class ProjectApiTest(TestCase):
	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def getAuthHeader(self, user):
		token = self.client.post('/oauth2/access_token/', {"client_id": self.oauth.client_id, "client_secret": self.oauth.client_secret, "grant_type": "password", "username": user, "password": user + "123"})
		auth_headers = {
			'Authorization': 'Oauth ' + json.loads(token.content).get('access_token'),
		}

		return auth_headers

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

		self.oauth = OAuthClient(user=eric, name="Test App", client_type=1, url="http://oliverroick.de")
		self.oauth.save()
		self.client = Client()
		self.singleSerializer = SingleSerializer()
		self.objectSerializer = ObjectSerializer()

	def test_projectsListWithCreator(self):
		response = self.client.get('/api/projects', HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("eric"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.deletedproject))
		

	def test_projectsListWithAdmin(self):
		response = self.client.get('/api/projects', HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("george"))
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithContributor(self):
		response = self.client.get('/api/projects', HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("diego"))
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithNonMember(self):
		response = self.client.get('/api/projects', HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("mehmet"))
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.privateproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.singleSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_singleProjectsWithCreator(self):
		response = self.client.get('/api/projects/' + str(self.publicproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("eric"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		
		response = self.client.get('/api/projects/' + str(self.privateproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("eric"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))

		response = self.client.get('/api/projects/' + str(self.inactiveproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("eric"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveproject))

		response = self.client.get('/api/projects/' + str(self.deletedproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("eric"))
		self.assertEqual(response.status_code, 404)
		
	def test_singleProjectsWithAdmin(self):
		response = self.client.get('/api/projects/' + str(self.publicproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("george"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		
		response = self.client.get('/api/projects/' + str(self.privateproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("george"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))

		response = self.client.get('/api/projects/' + str(self.inactiveproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("george"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveproject))

		response = self.client.get('/api/projects/' + str(self.deletedproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("george"))
		self.assertEqual(response.status_code, 404)


	def test_singleProjectsWithContributor(self):
		response = self.client.get('/api/projects/' + str(self.publicproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("diego"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		
		response = self.client.get('/api/projects/' + str(self.privateproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("diego"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateproject))

		response = self.client.get('/api/projects/' + str(self.inactiveproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("diego"))
		self.assertEqual(response.status_code, 401)

		response = self.client.get('/api/projects/' + str(self.deletedproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("diego"))
		self.assertEqual(response.status_code, 404)

	def test_singleProjectsWithNonMember(self):
		response = self.client.get('/api/projects/' + str(self.publicproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("mehmet"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicproject))
		
		response = self.client.get('/api/projects/' + str(self.privateproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("mehmet"))
		self.assertEqual(response.status_code, 401)

		response = self.client.get('/api/projects/' + str(self.inactiveproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("mehmet"))
		self.assertEqual(response.status_code, 401)

		response = self.client.get('/api/projects/' + str(self.deletedproject.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self.getAuthHeader("mehmet"))
		self.assertEqual(response.status_code, 404)
