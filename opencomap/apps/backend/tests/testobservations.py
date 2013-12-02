from django.test import TestCase
import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.feature import Feature
from opencomap.apps.backend.models.feature import Observation
from opencomap.apps.backend.models.featuretype import FeatureType
from opencomap.apps.backend.models.featuretype import TextField
from opencomap.apps.backend.models.featuretype import NumericField
from opencomap.apps.backend.models.featuretype import TrueFalseField
from opencomap.apps.backend.models.featuretype import LookupField
from opencomap.apps.backend.models.featuretype import LookupValue
from opencomap.apps.backend.models.choice import STATUS_TYPES

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError



class FeaturesTest(TestCase):
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

		admin = self._authenticate('eric')

		# Creating Project
		project = Factory.createProject('First Project', 'First Project description', admin)
		
		# Creating FeatureType
		featureType = FeatureType(name='Test Feature Type', project=project)
		featureType.save()
		
		# Creating example field types for each features
		textField = TextField(name='Text field', description='Text field description')
		featureType.addField(textField)
		numericField = NumericField(name='Numeric field', description='Numeric field description', required=True)
		featureType.addField(numericField)
		boolField = TrueFalseField(name='Bool field', description='Bool field description')
		featureType.addField(boolField)
		lookupField = LookupField(name='Lookup field', description='Lookup field description')
		featureType.addField(lookupField)
		lookupField.addLookupValues('Value 1', 'Value 2', 'Value 3')

		f = Feature(name='Example Feature', description='Example feature description', featuretype=featureType, creator=admin, geometry='POINT(-0.15003204345703125 51.55615526777012)')
		f.save()
		project.addFeature(f)

	def test_addObservation(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupField = feature.featuretype.getField('Lookup field').getLookupValues()[0]

		characteristics = {
			'Text field': 'This is test text',
			'Numeric field': 2,
			'Bool field': True,
			'Lookup field': lookupField.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)

		o = feature.getObservations()[0]
		self.assertEqual(o.getValue('Text field'), 'This is test text')
		self.assertEqual(o.getValue('Numeric field'), 2)
		self.assertEqual(o.getValue('Bool field'), True)
		self.assertEqual(o.getValue('Lookup field'), lookupField.id)

	def test_missingRequired(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]

		characteristics = {
			'Text field': 'This is test text',
			'Bool field': True
		}

		observation = Observation(creator=admin, data=characteristics)
		with self.assertRaises(ValidationError):
			feature.addObservation(observation)

		self.assertEqual(len(feature.getObservations()), 0)

	def test_invalidInput(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]

		characteristics = {
			'Numeric field': 2,
			'Bool field': 897098,
		}

		observation = Observation(creator=admin, data=characteristics)
		with self.assertRaises(ValidationError):
			feature.addObservation(observation)

		self.assertEqual(len(feature.getObservations()), 0)

	def test_invalidLookupVal(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupField = feature.featuretype.getField('Lookup field').getLookupValues()[0]

		characteristics = {
			'Numeric field': 2,
			'Lookup field': lookupField.id
		}

		observation = Observation(creator=admin, data=characteristics)
		with self.assertRaises(ValidationError):
			feature.addObservation(observation)

		self.assertEqual(len(feature.getObservations()), 0)

	def testUpdateData(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupField = feature.featuretype.getField('Lookup field').getLookupValues()[0]

		characteristics = {
			'Text field': 'This is test text',
			'Numeric field': 2,
			'Bool field': True,
			'Lookup field': lookupField.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)


		lookupField = feature.featuretype.getField('Lookup field').getLookupValues()[1]
		observation.setValue('Text field', 'update',)
		observation.setValue('Numeric field', 10)
		observation.setValue('Bool field', False)
		observation.setValue('Lookup field', lookupField.id)

		o = feature.getObservations()[0]
		self.assertEqual(o.getValue('Text field'), 'update')
		self.assertEqual(o.getValue('Numeric field'), 10)
		self.assertEqual(o.getValue('Bool field'), False)
		self.assertEqual(o.getValue('Lookup field'), lookupField.id)

	def testUpdateFalseData(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupField = feature.featuretype.getField('Lookup field').getLookupValues()[0]

		characteristics = {
			'Text field': 'This is test text',
			'Numeric field': 2,
			'Bool field': True,
			'Lookup field': lookupField.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)

		
		with self.assertRaises(ValidationError):
			observation.setValue('Numeric field', 'Kermit')
			observation.setValue('Lookup field', 564564548)

		o = feature.getObservations()[0]
		self.assertEqual(o.getValue('Text field'), 'This is test text')
		self.assertEqual(o.getValue('Numeric field'), 2)
		self.assertEqual(o.getValue('Bool field'), True)
		self.assertEqual(o.getValue('Lookup field'), lookupField.id)

	def testDeleteData(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupField = feature.featuretype.getField('Lookup field').getLookupValues()[0]

		characteristics = {
			'Text field': 'This is test text',
			'Numeric field': 2,
			'Bool field': True,
			'Lookup field': lookupField.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)

		
		with self.assertRaises(ValidationError):
			observation.deleteValue('Numeric field')

		observation.deleteValue('Text field')		

		o = feature.getObservations()[0]
		self.assertEqual(o.getValue('Numeric field'), 2)
		with self.assertRaises(KeyError):
			observation.getValue('Text field')
		