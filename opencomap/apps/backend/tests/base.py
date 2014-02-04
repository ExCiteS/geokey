
from django.test import TestCase

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.feature import Feature
from opencomap.apps.backend.models.view import View
from opencomap.apps.backend.models.viewgroup import ViewGroup
from opencomap.apps.backend.models.featuretype import FeatureType, TextField, NumericField, TrueFalseField, DateTimeField, LookupField, LookupValue
from opencomap.apps.backend.models.choice import STATUS_TYPES

class Test(TestCase):
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
		User.objects.create_user('zidane', 'zinedine@zidane.fr', 'zidane123', first_name='Zinedine', last_name='Zidane').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diego123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('carlos', 'carlos@valderama.co', 'carlos123', first_name='Carlos', last_name='Valderama').save()

		eric = self._authenticate('eric')
		george = self._authenticate('george')
		diego = self._authenticate('diego')
		carlos = self._authenticate('carlos')
		zidane = self._authenticate('zidane')

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

		self.active_view = View(name='Active View', description='Active view description', project=self.private_project, creator=eric)
		self.active_view.save()

		self.view_group = ViewGroup(name='Test Group', view=self.active_view, can_admin=True)
		self.view_group.save()
		self.view_group.addUsers(carlos)

		self.active_view_2 = View(name='Active View 2', description='Active view description', project=self.private_project, creator=eric)
		self.active_view_2.save()

		self.view_group_2 = ViewGroup(name='Test Group 2', view=self.active_view_2)
		self.view_group_2.save()
		self.view_group_2.addUsers(zidane)

		self.inactive_view = View(name='Inactive View', description='Inactive view description', project=self.private_project, creator=eric)
		self.inactive_view.save()
		self.inactive_view.delete()




		# self.featureType = FeatureType(name='Test Feature Type', description='Test featuretype description', project=self.public_project)
		# self.featureType.save()

		# self.textField = TextField(name='Text field', description='Text field description', featuretype=self.featureType)
		# self.textField.save()

		# self.numericField = NumericField(name='Numeric field', description='Numeric field description', required=True, featuretype=self.featureType)
		# self.numericField.save()

		# self.boolField = TrueFalseField(name='Bool field', description='Bool field description', featuretype=self.featureType)
		# self.boolField.save()

		# for i in range(len(self.geometries)):
		# 	f = Feature(name='Feature ' + str(i) , description='Feature ' + str(i) + ' description', featuretype=self.featureType, creator=eric, geometry=self.geometries[i])
		# 	f.save()
		# 	self.private_project.addFeature(f)