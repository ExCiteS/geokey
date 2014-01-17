from django.test import TestCase
from django.test.client import Client

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from provider.oauth2.models import Client as OAuthClient

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.libs.serializers import SingleSerializer, ObjectSerializer

from opencomap.apps.backend.models.featuretype import FeatureType, TextField, NumericField, DateTimeField, LookupField

import json

class ApiTest(TestCase):
	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def _getAuthHeader(self, user):
		token = self.client.post('/oauth2/access_token/', {"client_id": self.oauth.client_id, "client_secret": self.oauth.client_secret, "grant_type": "password", "username": user, "password": user + "123"})
		auth_headers = {
			'Authorization': 'Oauth ' + json.loads(token.content).get('access_token'),
		}

		return auth_headers

	def setUp(self):

		# ###################################
		# SETUP: USERS
		# ###################################

		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diego123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('carlos', 'carlos@valderama.de', 'carlos123', first_name='carlos', last_name='valderama').save()

		eric = self._authenticate('eric')
		george = self._authenticate('george')
		diego = self._authenticate('diego')
		carlos = self._authenticate('carlos')

		# ###################################
		# SETUP: CLIENTS AND SERIALIZER
		# ###################################

		self.client = Client()
		self.oauth = OAuthClient(user=eric, name="Test App", client_type=1, url="http://ucl.ac.uk")
		self.oauth.save()
		self.singleSerializer = SingleSerializer()
		self.objectSerializer = ObjectSerializer()

		# ###################################
		# SETUP: PROJECTS
		# ###################################

		self.publicproject = Factory.createProject('Public Project', 'Test description', eric)

		self.privateproject = Factory.createProject('Private Project', 'Test description', eric, isprivate=True)
		self.privateproject.admins.addUsers(george)
		self.privateproject.contributors.addUsers(diego)
		self.privateproject.save()

		self.inactiveproject = Factory.createProject('Inactive Project', 'Test description', eric)
		self.inactiveproject.admins.addUsers(george)
		self.inactiveproject.contributors.addUsers(diego)
		self.inactiveproject.update(status=STATUS_TYPES['INACTIVE'])

		self.deletedproject = Factory.createProject('Deleted Project', 'Test description', eric)
		self.deletedproject.delete()

		# ###################################
		# SETUP: FEATURE TYPES
		# ###################################
		
		
		self.publicFeatureType = FeatureType(name='Public feature type')
		self.publicproject.addFeatureType(self.publicFeatureType)
		textField = TextField(name='Text field', description='Text field description', featuretype=self.publicFeatureType)
		textField.save()
		numericField = NumericField(name='Numeric field', description='Numeric field description', required=True, featuretype=self.publicFeatureType)
		numericField.save()
		lookupField = LookupField(name='Lookup field', description='Lookup field description', featuretype=self.publicFeatureType)
		lookupField.save()
		lookupField.addLookupValues('Ms. Piggy', 'ist ein', 'dickes', 'Schwein')
		

		self.privateFeatureType = FeatureType(name='Private feature type')
		self.privateproject.addFeatureType(self.privateFeatureType)
		textField = TextField(name='Text field', description='Text field description', featuretype=self.privateFeatureType)
		textField.save()

		self.inactiveFeatureType = FeatureType(name='Invalid feature type')
		self.inactiveproject.addFeatureType(self.inactiveFeatureType)
		dateField = DateTimeField(name='Date Field', description='Date field description', featuretype=self.inactiveFeatureType)
		dateField.save()
		


	def get_request(self, url, user):
		return self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self._getAuthHeader(user))



