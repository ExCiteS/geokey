from django.test import TestCase
from opencomap.apps.backend.models.factory import Factory
from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.fields import FeatureType
from opencomap.apps.backend.models.fields import Field
from opencomap.apps.backend.models.fields import LookupField
from opencomap.apps.backend.models.fields import LookupValue
from opencomap.apps.backend.models.choices import FIELD_TYPES
from opencomap.apps.backend.models.choices import STATUS_TYPES

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class FeatureTypeTest(TestCase):
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
		project = Factory().createProject('Test Project', 'Test description', admin)

	def test_createAndRemoveFields(self):
		admin = self._authenticate('eric')

		project = Project.objects.all()[0]
		featureType = FeatureType(name='Test Feature Type', project=project)
		featureType.save()

		# Test create and add fields
		textField = Field(name='Text field', description='Text field description', fieldtype=FIELD_TYPES['TEXT'], featuretype=featureType)
		textField.save()
		self.assertEqual(textField.name, 'Text field')
		self.assertFalse(textField.required)
		self.assertEqual(textField.status, STATUS_TYPES['ACTIVE'])

		numericField = Field(name='Numeric field', description='Numeric field description', required=True, fieldtype=FIELD_TYPES['NUMERIC'], featuretype=featureType)
		numericField.save()
		self.assertEqual(numericField.name, 'Numeric field')
		self.assertTrue(numericField.required)
		self.assertEqual(numericField.status, STATUS_TYPES['ACTIVE'])

		dateField = Field(name='Date field', description='Date field description', fieldtype=FIELD_TYPES['DATE_TIME'], featuretype=featureType)
		dateField.save()
		self.assertEqual(dateField.name, 'Date field')
		self.assertFalse(dateField.required)
		self.assertEqual(dateField.status, STATUS_TYPES['ACTIVE'])

		boolField = Field(name='Bool field', description='Bool field description', fieldtype=FIELD_TYPES['TRUE_FALSE'], featuretype=featureType)
		boolField.save()
		self.assertEqual(boolField.name, 'Bool field')
		self.assertFalse(boolField.required)
		self.assertEqual(boolField.status, STATUS_TYPES['ACTIVE'])

		self.assertEqual(len(featureType.getFields()), 4)

		# Test remove fields
		featureType.removeFields(dateField, boolField)
		self.assertEqual(len(featureType.getFields()), 2)
		for field in featureType.getFields():
			self.assertIn(field, (textField, numericField))

	def test_createAndRemoveLookup(self):
		admin = self._authenticate('eric')

		project = Project.objects.all()[0]
		featureType = FeatureType(name='Test Feature Type', project=project)
		featureType.save()

		lookupField = LookupField(name='Lookup field', description='Lookup field description', featuretype=featureType)
		lookupField.save()

		self.assertEqual(len(featureType.getFields()), 1)

		lookupField.addLookupValues('Value 1', 'Value 2', 'Value 3')

		self.assertEqual(lookupField.name, 'Lookup field')
		self.assertFalse(lookupField.required)
		self.assertEqual(lookupField.status, STATUS_TYPES['ACTIVE'])

		self.assertEqual(len(lookupField.getLookupValues()), 3)
		
		valueToRemove = lookupField.getLookupValues()[0]
		lookupField.removeLookupValues(valueToRemove)
		self.assertEqual(len(lookupField.getLookupValues()), 2)
		for lookup in lookupField.getLookupValues():
			self.assertNotEqual(lookup, valueToRemove)