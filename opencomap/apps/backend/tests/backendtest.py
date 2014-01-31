from django.test import TestCase

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.feature import Feature
from opencomap.apps.backend.models.featuretype import TextField, NumericField, TrueFalseField, DateTimeField, LookupField, LookupValue

class BackendTest(TestCase):
	class Meta: 
		app_label = 'backend'

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

	def setUp(self):
		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('zidane', 'zinedine@zidane.fr', 'zinedine123', first_name='Zinedine', last_name='Zidane').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diegoe123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('carlos', 'carlos@valderama.co', 'carlos123', first_name='Carlos', last_name='Valderama').save()

		admin = self._authenticate('eric')
		self.project = Factory.createProject('Test Project', 'Test description', admin)
		self.featureType = Factory.createFeaturetype('Test Feature Type', 'Test featuretype description', admin, self.project)

		self.textField = TextField(name='Text field', description='Text field description', featuretype=self.featureType)
		self.textField.save()

		self.numericField = NumericField(name='Numeric field', description='Numeric field description', required=True, featuretype=self.featureType)
		self.numericField.save()

		self.boolField = TrueFalseField(name='Bool field', description='Bool field description', featuretype=self.featureType)
		self.boolField.save()

		for i in range(len(self.geometries)):
			f = Feature(name='Feature ' + str(i) , description='Feature ' + str(i) + ' description', featuretype=self.featureType, creator=admin, geometry=self.geometries[i])
			f.save()
			self.project.addFeature(f)