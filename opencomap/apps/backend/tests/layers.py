from django.test import TestCase

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.layers import Layer
from opencomap.apps.backend.models.fields import Field
from opencomap.apps.backend.models.fields import LookupField
from opencomap.apps.backend.models.fields import LookupValue
from opencomap.apps.backend.models.choices import STATUS_TYPES

# class LayersTest(TestCase):
# 	class Meta: 
# 		app_label = 'backend'

# 	def _authenticate(self, name):
# 		return authenticate(username=name, password=name + '123')

# 	def setUp(self):
# 		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
# 		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
# 		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
# 		User.objects.create_user('zidane', 'zinedine@zidane.fr', 'zinedine123', first_name='Zinedine', last_name='Zidane').save()
# 		User.objects.create_user('diego', 'diego@maradonna.ar', 'diegoe123', first_name='Diego', last_name='Maradonna').save()
# 		User.objects.create_user('carlos', 'carlos@valderama.co', 'carlos123', first_name='Carlos', last_name='Valderama').save()

# 	def test_removeLookups(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		lookupField = LookupField(name='Lookup', description='A lookup field', required=True)
# 		textField = TextField(name='Text', description='A text field', required=True)
# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
# 		layer1.addFields(admin, lookupField, textField)
# 		lookupField.addLookupValues(admin, 'value 1', 'value 2', 'value 3')

# 		lookups = LookupValue.objects.filter(field__id__exact=lookupField.id)
# 		with self.assertRaises(PermissionDenied):
# 			lookupField.removeLookupValues(user, lookups[0])

# 		lookupName = lookups[0].name
# 		lookupField.removeLookupValues(admin, lookups[0])
# 		self.assertEqual(len(LookupValue.objects.filter(field__id__exact=lookupField.id)), 2)
# 		for value in LookupValue.objects.filter(field__id__exact=lookupField.id):
# 			self.assertNotEqual(value.name, lookupName)

# 	def test_addLookups(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		lookupField = LookupField(name='Lookup', description='A lookup field', required=True)
# 		textField = TextField(name='Text', description='A text field', required=True)
# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
# 		layer1.addFields(admin, lookupField, textField)

# 		lookupField.addLookupValues(admin, 'value 1', 'value 2', 'value 3')
# 		self.assertEqual(len(LookupValue.objects.filter(field__id__exact=lookupField.id)), 3)
# 		for value in LookupValue.objects.filter(field__id__exact=lookupField.id):
# 			self.assertIn(value.name, ('value 1', 'value 2', 'value 3'))

# 		with self.assertRaises(PermissionDenied):
# 			lookupField.addLookupValues(user, 'value 1', 'value 2')		

# 	def test_updateFields(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		textField = TextField(name='Text', description='A text field', required=True)
# 		numericField = NumericField(name='Numberic', description='A numeric field',required=True)
# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)

# 		layer1.addFields(admin, textField, numericField)

# 		textField.update(admin, name='Updated TextField')
# 		self.assertEqual(textField.name, 'Updated TextField')

# 		with self.assertRaises(PermissionDenied):
# 			numericField.update(user, name='Updated Numberic Field')


# 	def test_removeFields(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		textField = TextField(name='Text', description='A text field', required=True)
# 		numericField = NumericField(name='Numberic', description='A numeric field',required=True)
# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
# 		layer1.addFields(admin, textField, numericField)

# 		layer1.removeFields(admin, textField)
# 		self.assertEqual(len(Field.objects.filter(layer__id__exact=layer1.id)), 1)

# 		for field in Field.objects.filter(layer__id__exact=layer1.id):
# 			self.assertEqual(field.id, numericField.id)

# 		# try to add field without permissions
# 		with self.assertRaises(PermissionDenied):
# 			layer1.removeFields(user, numericField)

# 	def test_addFields(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		textField = TextField(name='Text', description='A text field', required=True)
# 		numericField = NumericField(name='Numberic', description='A numeric field',required=True)
# 		dateField = DateTimeField(name='Date/Time', description='A date/time field', required=True)
# 		lookupField = LookupField(name='Lookup', description='A lookup field', required=True)
# 		booleanField = TrueFalseField(name='Bool', description='A true/false field', required=True)

# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)

# 		# add single field
# 		layer1.addFields(admin, textField)
# 		self.assertEqual(len(Field.objects.filter(layer__id__exact=layer1.id)), 1)

# 		# add more than one fields
# 		layer1.addFields(admin, numericField, dateField, lookupField)
# 		self.assertEqual(len(Field.objects.filter(layer__id__exact=layer1.id)), 4)
# 		for field in Field.objects.filter(layer__id__exact=layer1.id):
# 			self.assertEqual(layer1, field.layer)

# 		# try to add field without permissions
# 		with self.assertRaises(PermissionDenied):
# 			layer1.addFields(user, booleanField)

# 	def test_updateLayer(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
# 		with self.assertRaises(PermissionDenied):
# 			layer1.update(user, name='Updated Test Layer 1')

# 		layer1.update(admin, name='Updated Test Layer 1')
# 		self.assertEqual(layer1.name, 'Updated Test Layer 1')

# 	def test_status(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		activelayer = LayerFactory('Active', 'Lorem ipsum dolor sit amet', admin)
# 		reviewlayer = LayerFactory('Review', 'Lorem ipsum dolor sit amet', admin)
# 		retiredlayer = LayerFactory('Retired', 'Lorem ipsum dolor sit amet', admin)
# 		removedlayer = LayerFactory('Removed', 'Lorem ipsum dolor sit amet', admin)
# 		project1 = ProjectFactory('Test Project 1', 'Lorem ipsum dolor sit amet', admin)

# 		with self.assertRaises(PermissionDenied):
# 			reviewlayer.setStatus(user, STATUS_TYPES['REVIEW'])

# 		reviewlayer.setStatus(admin, STATUS_TYPES['REVIEW'])
# 		retiredlayer.setStatus(admin, STATUS_TYPES['RETIRED'])
# 		removedlayer.setStatus(admin, STATUS_TYPES['DELETED'])

# 		project1.addLayers(admin, activelayer, reviewlayer, retiredlayer, removedlayer)
# 		self.assertEqual(len(project1.getLayers(admin)), 2)
# 		for layer in project1.getLayers(admin):
# 			self.assertIn(layer.name, ('Active', 'Review'))


# 	def test_Permissions(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
# 		project1 = ProjectFactory('Test Project 1', 'Lorem ipsum dolor sit amet', admin)

# 		self.assertTrue(layer1.userCanView(admin))
# 		self.assertTrue(layer1.userCanEdit(admin))
# 		self.assertTrue(layer1.userCanAdmin(admin))
# 		self.assertTrue(layer1.userCanContribute(admin))

# 		self.assertTrue(layer1.userCanView(user))
# 		self.assertFalse(layer1.userCanEdit(user))
# 		self.assertFalse(layer1.userCanAdmin(user))
# 		self.assertFalse(layer1.userCanContribute(user))

# 	def test_removeFromProject(self):
# 		admin = self._authenticate('eric')
# 		user = self._authenticate('george')

# 		project1 = ProjectFactory('Test Project 1', 'Lorem ipsum dolor sit amet', admin)
# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
# 		project1.addLayers(admin, layer1)
		
# 		with self.assertRaises(PermissionDenied):
# 			project1.removeLayers(user, layer1)

# 		project1.removeLayers(admin, layer1)
# 		self.assertEqual(len(project1.getLayers(admin)), 0)

# 	def test_assignToProject(self):
# 		admin = self._authenticate('eric')

# 		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
# 		layer2 = LayerFactory('Test Layer 2', 'Lorem ipsum dolor sit amet', admin)
# 		layer3 = LayerFactory('Test Layer 3', 'Lorem ipsum dolor sit amet', admin)
# 		project1 = ProjectFactory('Test Project 1', 'Lorem ipsum dolor sit amet', admin)

# 		project1.addLayers(admin, layer1)
# 		self.assertEqual(len(project1.getLayers(admin)), 1)
# 		self.assertIn(project1, project1.getLayers(admin)[0].projects.all())

# 		project1.addLayers(admin, layer2, layer3)
# 		self.assertEqual(len(project1.getLayers(admin)), 3)
# 		for layer in project1.getLayers(admin):
# 			self.assertIn(layer, (layer1, layer2, layer3))

# 	def test_createLayer(self):
# 		user = self._authenticate('eric')

# 		layer = LayerFactory('Test Layer', 'Lorem ipsum dolor sit amet', user)
# 		self.assertEqual(layer.creator, user)

# 		for group in layer.usergroups.all():
# 			self.assertIn(group.name, ('Admin', 'General public'))
# 			if (group.name == 'Admin'):
# 				self.assertEqual(len(group.users.all()), 1)
# 				self.assertEqual(group.users.all()[0], user)