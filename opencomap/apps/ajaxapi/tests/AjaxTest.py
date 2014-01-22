from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import json

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.featuretype import FeatureType, TextField, LookupField
from opencomap.apps.backend.models.viewgroup import ViewGroup
from opencomap.libs.serializers import ObjectSerializer, FeatureTypeSerializer



class AjaxTest(TestCase):
	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def setUp(self):
		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diego123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('carlos', 'carlos@valderama.de', 'carlos123', first_name='carlos', last_name='valderama').save()
		User.objects.create_user('peter', 'peter@schmeichel.dk', 'peter123', first_name='peter', last_name='schmeichel').save()

		eric = self._authenticate('eric')
		george = self._authenticate('george')
		diego = self._authenticate('diego')
		carlos = self._authenticate('carlos')
		peter = self._authenticate('peter')

		self.project = Factory.createProject('Project', 'Test description', eric, isprivate=True)
		self.project.admins.addUsers(george)
		self.project.contributors.addUsers(diego)
		self.project.save()

		self.featureType = Factory.createFeaturetype('Feature type', 'TFeature type description', eric, self.project)
		self.field = TextField(name='Text field', description='Text field description', featuretype=self.featureType)
		self.field.save()

		self.lookupfield = LookupField(name='Lookup field', description='Lookup field description', featuretype=self.featureType)
		self.lookupfield.save()
		self.lookupfield.addLookupValues('Gonzo')
		self.lookupvalue = self.lookupfield.lookupvalue_set.filter(name='Gonzo')[0]
		self.lookupvalue.status = 1
		self.lookupvalue.save()

		self.viewgroup = ViewGroup(name='View Group')
		self.project.getViews()[0].addUserGroup(self.viewgroup)
		self.viewgroup.addUsers(peter)

		testProject = Factory.createProject('Test Project', 'Test description', carlos)
		self.referenceGroup = testProject.admins
		self.client = Client()

		self.objectSerializer = ObjectSerializer()
		self.featureTypeSerializer = FeatureTypeSerializer()

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