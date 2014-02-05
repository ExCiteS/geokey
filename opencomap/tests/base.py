from django.test import TestCase
from django.test.client import Client
from provider.oauth2.models import Client as OAuthClient

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import json

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.feature import Feature
from opencomap.apps.backend.models.view import View
from opencomap.apps.backend.models.viewgroup import ViewGroup
from opencomap.apps.backend.models.featuretype import FeatureType, TextField, NumericField, TrueFalseField, DateTimeField, LookupField, LookupValue
from opencomap.apps.backend.models.choice import STATUS_TYPES

from opencomap.libs.serializers import ObjectSerializer

class CommunityMapsTest(TestCase):
	geometries = [
		'POINT(-0.15003204345703125 51.55615526777012)',
		'POINT(-0.1544952392578125 51.53074643430678)',
		'POINT(-0.17234802246093747 51.50446860957782)',
		'POINT(-0.11398315429687499 51.52967852566193)',
		'POINT(-0.13149261474609375 51.4950647301436)',
		'POINT(-0.0391387939453125 51.53800754877571)',
		'POINT(-0.06326794624328613 51.55791627866145)',
		'POINT(-0.11020660400390625 51.505750806437874)',
		'POINT(0.00308990478515625 51.50040808149318)',
		'POINT(-0.06557464599609375 51.52562024435108)'
	]

	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def _getAuthHeader(self, user):
		token = self.client.post('/oauth2/access_token/', {"client_id": self.oauth.client_id, "client_secret": self.oauth.client_secret, "grant_type": "password", "username": user, "password": user + "123"})
		auth_headers = {
			'Authorization': 'Oauth ' + json.loads(token.content).get('access_token'),
		}

		return auth_headers

	def setUp(self):
		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('zidane', 'zinedine@zidane.fr', 'zidane123', first_name='Zinedine', last_name='Zidane').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diego123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('carlos', 'carlos@valderama.co', 'carlos123', first_name='Carlos', last_name='Valderama').save()
		User.objects.create_user('luis', 'luis@figo.pt', 'luis123', first_name='Luis', last_name='Figo').save()
		User.objects.create_user('peter', 'peter@schmeichel.dk', 'peter123', first_name='Peter', last_name='Schmeichel').save()

		eric = self._authenticate('eric')
		george = self._authenticate('george')
		diego = self._authenticate('diego')
		carlos = self._authenticate('carlos')
		zidane = self._authenticate('zidane')
		luis = self._authenticate('luis')
		peter = self._authenticate('peter')

		##################################
		# Helpers
		##################################

		self.client = Client()

		self.oauth = OAuthClient(user=eric, name="Test App", client_type=1, url="http://ucl.ac.uk")
		self.oauth.save()

		self.objectSerializer = ObjectSerializer()


		##################################
		# Set up projects
		##################################

		self.public_project = Factory.createProject('Public project', 'Test description', eric)
		self.public_project.save()

		self.inactive_project = Factory.createProject('Inactive project', 'Test description', eric)
		self.inactive_project.status = STATUS_TYPES['INACTIVE']
		self.inactive_project.admins.addUsers(george)
		self.inactive_project.save()

		self.private_project = Factory.createProject('Private project', 'Test description', eric, isprivate=True)
		self.private_project.admins.addUsers(george)
		self.private_project.contributors.addUsers(diego)
		self.private_project.save()

		self.deleted_project = Factory.createProject('Deleted project', 'Test description', eric)
		self.deleted_project.save()
		self.deleted_project.delete()

		##################################
		# Set up views and user groups
		##################################
		
		self.referenceGroup = self.deleted_project.admins

		self.active_view = View(name='Active View', description='Active view description', project=self.private_project, creator=eric)
		self.active_view.save()

		self.active_view_group = ViewGroup(name='Active View Group', view=self.active_view)
		self.active_view_group.save()
		self.active_view_group.addUsers(carlos, peter)

		self.active_view_two = View(name='Active View 2', description='Active view 2 description', project=self.private_project, creator=eric)
		self.active_view_two.save()

		self.active_view_group_two = ViewGroup(name='Active View Group', view=self.active_view_two)
		self.active_view_group_two.save()
		self.active_view_group_two.addUsers(luis)

		self.deleted_view = View(name='Deleted View', description='Deleted view description', project=self.private_project, creator=eric)
		self.deleted_view.save()

		self.deleted_view_group = ViewGroup(name='Deleted View Group', view=self.deleted_view)
		self.deleted_view_group.save()
		self.deleted_view_group.addUsers(zidane)
		self.deleted_view.delete()

		##################################
		# Feature types and fields
		##################################

		self.active_feature_type = FeatureType(name='Feature type', description='Feature type description', project=self.private_project)
		self.active_feature_type.save()

		self.text_field = TextField(name='Text field', description='Text field description', featuretype=self.active_feature_type)
		self.text_field.save()

		self.lookupfield = LookupField(name='Lookup field', description='Lookup field description', featuretype=self.active_feature_type)
		self.lookupfield.save()
		self.lookupfield.addLookupValues('Gonzo')
		self.lookupvalue = self.lookupfield.lookupvalue_set.filter(name='Gonzo')[0]

		self.inactive_field = TextField(name='Inactive', description='description', featuretype=self.active_feature_type, status=STATUS_TYPES['INACTIVE'])
		self.inactive_field.save()

		self.inactive_feature_type = FeatureType(name='Inactive feature type', description='description', project=self.private_project, status=STATUS_TYPES['INACTIVE'])
		self.inactive_feature_type.save()
		dateField = DateTimeField(name='Date Field', description='Date field description', featuretype=self.inactive_feature_type)
		dateField.save()

		self.inactive_feature_type_two = FeatureType(name='Inactive feature type', description='description', project=self.inactive_project, status=STATUS_TYPES['INACTIVE'])
		self.inactive_feature_type_two.save()


		self.public_feature_type = FeatureType(name='Public feature type', description='description', project=self.public_project)
		self.public_feature_type.save()
		textField = TextField(name='Text field', description='Text field description', featuretype=self.public_feature_type)
		textField.save()
		numericField = NumericField(name='Numeric field', description='Numeric field description', required=True, featuretype=self.public_feature_type)
		numericField.save()
		lookupField = LookupField(name='Lookup field', description='Lookup field description', featuretype=self.public_feature_type)
		lookupField.save()
		lookupField.addLookupValues('Ms. Piggy', 'ist ein', 'dickes', 'Schwein')


		self.private_feature_type = FeatureType(name='Private feature type', description='description', project=self.private_project)
		self.private_feature_type.save()
		textField = TextField(name='Text field', description='Text field description', featuretype=self.private_feature_type)
		textField.save()

	def get(self, url, user):
		self.client.login(username=user, password=user + '123')
		return self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')

	def post(self, url, data, user):
		self.client.login(username=user, password=user + '123')
		return self.client.post(url, json.dumps(data), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')

	def put(self, url, data, user):
		self.client.login(username=user, password=user + '123')
		return self.client.put(url, json.dumps(data), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')

	def delete(self, url, user):
		self.client.login(username=user, password=user + '123')
		return self.client.delete(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')

	def get_with_oauth(self, url, user):
		return self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest', **self._getAuthHeader(user))