from django.test import TestCase
import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.feature import Feature
from opencomap.apps.backend.models.featuretype import FeatureType
from opencomap.apps.backend.models.featuretype import TextField
from opencomap.apps.backend.models.featuretype import NumericField
from opencomap.apps.backend.models.featuretype import TrueFalseField
from opencomap.apps.backend.models.featuretype import LookupField
from opencomap.apps.backend.models.featuretype import LookupValue
from opencomap.apps.backend.models.choice import STATUS_TYPES

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
		project = Factory.createProject('Test Project', 'Test description', admin)

	def test_createAndRemoveFields(self):
		admin = self._authenticate('eric')

		project = Project.objects.all()[0]
		featureType = FeatureType(name='Test Feature Type')
		project.addFeatureType(featureType)

		# Test create and add fields
		textField = TextField(name='Text field', description='Text field description', featuretype=featureType)
		textField.save()
		self.assertEqual(textField.name, 'Text field')
		self.assertFalse(textField.required)
		self.assertEqual(textField.status, STATUS_TYPES['ACTIVE'])

		numericField = NumericField(name='Numeric field', description='Numeric field description', required=True, featuretype=featureType)
		numericField.save()
		self.assertEqual(numericField.name, 'Numeric field')
		self.assertTrue(numericField.required)
		self.assertEqual(numericField.status, STATUS_TYPES['ACTIVE'])

		boolField = TrueFalseField(name='Bool field', description='Bool field description', featuretype=featureType)
		boolField.save()
		self.assertEqual(boolField.name, 'Bool field')
		self.assertFalse(boolField.required)
		self.assertEqual(boolField.status, STATUS_TYPES['ACTIVE'])

		self.assertEqual(len(featureType.getFields()), 3)

		# Test remove fields
		featureType.removeFields(textField, boolField)
		self.assertEqual(len(featureType.getFields()), 1)
		for field in featureType.getFields():
			self.assertEqual(field.id, numericField.field_ptr_id)

	def test_createAndRemoveLookup(self):
		admin = self._authenticate('eric')

		project = Project.objects.all()[0]
		featureType = FeatureType(name='Test Feature Type')
		project.addFeatureType(featureType)

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

	def test_textValidation(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		featureType = FeatureType(name='Test Feature Type')
		project.addFeatureType(featureType)

		textField = TextField(name='Text field', description='Text field description', featuretype=featureType)
		textField.save()

		self.assertTrue(textField.validateInput('This is a test text'))
		self.assertTrue(textField.validateInput(str(2)))
		self.assertFalse(textField.validateInput(2))
		self.assertFalse(textField.validateInput(True))
		self.assertFalse(textField.validateInput(False))

	def test_numericValidation(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		featureType = FeatureType(name='Test Feature Type')
		project.addFeatureType(featureType)

		numericField = NumericField(name='Numeric field', description='Numeric field description', required=True, featuretype=featureType)
		numericField.save()

		self.assertFalse(numericField.validateInput('This is a test text'))
		self.assertTrue(numericField.validateInput('2'))
		self.assertTrue(numericField.validateInput('-102'))
		self.assertTrue(numericField.validateInput('327.498'))
		self.assertTrue(numericField.validateInput('-435345.87324'))
		self.assertTrue(numericField.validateInput(2))
		self.assertTrue(numericField.validateInput(2.324))
		self.assertTrue(numericField.validateInput(-2134))
		self.assertTrue(numericField.validateInput(-213247.8327))
		self.assertFalse(numericField.validateInput(True))
		self.assertFalse(numericField.validateInput(False))

		numericRange1 = NumericField(name='Numeric field', description='Numeric field description', minval=10, required=True, featuretype=featureType)
		numericRange1.save()
		self.assertTrue(numericRange1.validateInput(546.5347))
		self.assertTrue(numericRange1.validateInput(12))
		self.assertFalse(numericRange1.validateInput(2.324))
		self.assertFalse(numericRange1.validateInput(-2134))
		self.assertTrue(numericRange1.validateInput('546.5347'))
		self.assertTrue(numericRange1.validateInput('12'))
		self.assertFalse(numericRange1.validateInput('2.324'))
		self.assertFalse(numericRange1.validateInput('-2134'))

		numericRange2 = NumericField(name='Numeric field', description='Numeric field description', maxval=87, required=True, featuretype=featureType)
		numericRange2.save()
		self.assertFalse(numericRange2.validateInput(546.5347))
		self.assertTrue(numericRange2.validateInput(12))
		self.assertTrue(numericRange2.validateInput(2.324))
		self.assertTrue(numericRange2.validateInput(-2134))
		self.assertFalse(numericRange2.validateInput('546.5347'))
		self.assertTrue(numericRange2.validateInput('12'))
		self.assertTrue(numericRange2.validateInput('2.324'))
		self.assertTrue(numericRange2.validateInput('-2134'))

		numericRange3 = NumericField(name='Numeric field', description='Numeric field description', minval=10, maxval=87, required=True, featuretype=featureType)
		numericRange3.save()
		self.assertFalse(numericRange3.validateInput(546.5347))
		self.assertTrue(numericRange3.validateInput(12))
		self.assertFalse(numericRange3.validateInput(2.324))
		self.assertFalse(numericRange3.validateInput(-2134))
		self.assertFalse(numericRange3.validateInput('546.5347'))
		self.assertTrue(numericRange3.validateInput('12'))
		self.assertFalse(numericRange3.validateInput('2.324'))
		self.assertFalse(numericRange3.validateInput('-2134'))

	def test_truefalseValidation(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		featureType = FeatureType(name='Test Feature Type')
		project.addFeatureType(featureType)

		boolField = TrueFalseField(name='Bool field', description='Bool field description', featuretype=featureType)
		boolField.save()

		self.assertFalse(boolField.validateInput('This is a test text'))
		self.assertFalse(boolField.validateInput('2'))
		self.assertFalse(boolField.validateInput(2))
		self.assertTrue(boolField.validateInput(True))
		self.assertTrue(boolField.validateInput(False))
		self.assertTrue(boolField.validateInput('True'))
		self.assertTrue(boolField.validateInput('true'))
		self.assertTrue(boolField.validateInput('1'))
		self.assertTrue(boolField.validateInput('t'))
		self.assertTrue(boolField.validateInput('False'))
		self.assertTrue(boolField.validateInput('false'))
		self.assertTrue(boolField.validateInput('0'))
		self.assertTrue(boolField.validateInput('f'))
		self.assertTrue(boolField.validateInput(0))
		self.assertTrue(boolField.validateInput(1))

	def test_lookupValidation(self):
		admin = self._authenticate('eric')
		project = Project.objects.all()[0]
		featureType = FeatureType(name='Test Feature Type')
		project.addFeatureType(featureType)

		lookupField = LookupField(name='Lookup field', description='Lookup field description', featuretype=featureType)
		lookupField.save()

		lookupField.addLookupValues('Ms. Piggy', 'ist ein', 'dickes', 'Schwein')

		for lookupValue in featureType.getField('Lookup field').getLookupValues():
			self.assertTrue(lookupField.validateInput(lookupValue.id))			

		self.assertFalse(lookupField.validateInput('Kermit'))
		self.assertFalse(lookupField.validateInput(287894))