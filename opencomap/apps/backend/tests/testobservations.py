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
		self.textField = TextField(name='Text field', description='Text field description')
		featureType.addField(self.textField)
		
		self.numericField = NumericField(name='Numeric field', description='Numeric field description', required=True)
		featureType.addField(self.numericField)
		
		self.boolField = TrueFalseField(name='Bool field', description='Bool field description')
		featureType.addField(self.boolField)

		self.lookupField = LookupField(name='Lookup field', description='Lookup field description')
		featureType.addField(self.lookupField)
		self.lookupField.addLookupValues('Value 1', 'Value 2', 'Value 3')

		f = Feature(name='Example Feature', description='Example feature description', featuretype=featureType, creator=admin, geometry='POINT(-0.15003204345703125 51.55615526777012)')
		f.save()
		project.addFeature(f)

	def test_addObservation(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupValue = self.lookupField.getInstance().getLookupValues()[0]

		characteristics = {
			str(self.textField.id): 'This is test text',
			str(self.numericField.id): 2,
			str(self.boolField.id): True,
			str(self.lookupField.id): lookupValue.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)

		o = feature.getObservations()[0]
		self.assertEqual(o.getValue(self.textField.id), 'This is test text')
		self.assertEqual(o.getValue(self.numericField.id), 2)
		self.assertEqual(o.getValue(self.boolField.id), True)
		self.assertEqual(o.getValue(self.lookupField.id), lookupValue.id)

	def test_updateObservation(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupValue = self.lookupField.getInstance().getLookupValues()[0]

		characteristics = {
			str(self.textField.id): 'This is test text',
			str(self.numericField.id): 2,
			str(self.boolField.id): True,
			str(self.lookupField.id): lookupValue.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)

		o = feature.getObservations()[0]

		with self.assertRaises(ValidationError):
			o.update(status=STATUS_TYPES['DELETED'])
		
		o.update(status=STATUS_TYPES['REVIEW'])


	def test_missingRequired(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]

		characteristics = {
			str(self.textField.id): 'This is test text',
			str(self.boolField.id): True
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
			str(self.numericField.id): 2,
			str(self.boolField.id): 897098,
		}

		observation = Observation(creator=admin, data=characteristics)
		with self.assertRaises(ValidationError):
			feature.addObservation(observation)

		self.assertEqual(len(feature.getObservations()), 0)

	def test_invalidLookupVal(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupValue = self.lookupField.getInstance().getLookupValues()[0]

		characteristics = {
			str(self.numericField.id): 2,
			str(self.boolField.id): lookupValue.id
		}

		observation = Observation(creator=admin, data=characteristics)
		with self.assertRaises(ValidationError):
			feature.addObservation(observation)

		self.assertEqual(len(feature.getObservations()), 0)

	def testUpdateData(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupValue = self.lookupField.getInstance().getLookupValues()[0]

		characteristics = {
			str(self.textField.id): 'This is test text',
			str(self.numericField.id): 2,
			str(self.boolField.id): True,
			str(self.lookupField.id): lookupValue.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)


		lookupValue = self.lookupField.getInstance().getLookupValues()[1]
		observation.setValue(self.textField.id, 'update',)
		observation.setValue(self.numericField.id, 10)
		observation.setValue(self.boolField.id, False)
		observation.setValue(self.lookupField.id, lookupValue.id)

		o = feature.getObservations()[0]
		self.assertEqual(o.getValue(self.textField.id), 'update')
		self.assertEqual(o.getValue(self.numericField.id), 10)
		self.assertEqual(o.getValue(self.boolField.id), False)
		self.assertEqual(o.getValue(self.lookupField.id), lookupValue.id)

	def testUpdateFalseData(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupValue = self.lookupField.getInstance().getLookupValues()[0]

		characteristics = {
			str(self.textField.id): 'This is test text',
			str(self.numericField.id): 2,
			str(self.boolField.id): True,
			str(self.lookupField.id): lookupValue.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)

		
		with self.assertRaises(ValidationError):
			observation.setValue(self.numericField.id, 'Kermit')
			observation.setValue(self.lookupField.id, 564564548)

		o = feature.getObservations()[0]
		self.assertEqual(o.getValue(self.textField.id), 'This is test text')
		self.assertEqual(o.getValue(self.numericField.id), 2)
		self.assertEqual(o.getValue(self.boolField.id), True)
		self.assertEqual(o.getValue(self.lookupField.id), lookupValue.id)

	def testDeleteData(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		feature = project.getFeatures()[0]
		lookupValue = self.lookupField.getInstance().getLookupValues()[0]

		characteristics = {
			str(self.textField.id): 'This is test text',
			str(self.numericField.id): 2,
			str(self.boolField.id): True,
			str(self.lookupField.id): lookupValue.id
		}

		observation = Observation(creator=admin, data=characteristics)
		feature.addObservation(observation)

		
		with self.assertRaises(ValidationError):
			observation.deleteValue(self.numericField.id)

		observation.deleteValue(self.textField.id)		

		o = feature.getObservations()[0]
		self.assertEqual(o.getValue(self.numericField.id), 2)
		with self.assertRaises(KeyError):
			observation.getValue(self.textField.id)
		