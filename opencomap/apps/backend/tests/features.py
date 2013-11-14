from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.layers import Layer
from opencomap.apps.backend.models.permissions import UserGroup
from opencomap.apps.backend.models.features import Feature
from opencomap.apps.backend.models.choices import STATUS_TYPES

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

	def test_setStatus(self):
		admin = self._authenticate('eric')
		user = self._authenticate('george')

		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
		feature1 = Feature(name='Feature 1', description='Feature 1 description', creator=user, geometry='POINT(-0.1341533660888672 51.52459226699835)')
		feature2 = Feature(name='Feature 2', description='Feature 2 description', creator=admin, geometry='POINT(-0.15192031860351562 51.5538605149062)')
		feature3 = Feature(name='Feature 3', description='Feature 3 description', creator=contributor, geometry='POINT(-0.0766897201538086 51.52388468468649)')
		layer1.addFeatures(admin, feature1, feature2, feature3)

		self.assertEqual(len(layer1.getFeatures(admin)), 3)

		feature1.setStatus(admin, STATUS_TYPES['RETIRED'])
		self.assertEqual(len(layer1.getFeatures(admin)), 2)
		for feature in layer1.getFeatures(admin):
			self.assertIn(feature, (feature2, feature3))

	def test_deleteFeature(self):
		admin = self._authenticate('eric')
		user = self._authenticate('george')

		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
		feature1 = Feature(name='Feature 1', description='Feature 1 description', creator=user, geometry='POINT(-0.1341533660888672 51.52459226699835)')
		feature2 = Feature(name='Feature 2', description='Feature 2 description', creator=admin, geometry='POINT(-0.15192031860351562 51.5538605149062)')
		feature3 = Feature(name='Feature 3', description='Feature 3 description', creator=contributor, geometry='POINT(-0.0766897201538086 51.52388468468649)')
		layer1.addFeatures(admin, feature1, feature2, feature3)

		self.assertEqual(len(layer1.getFeatures(admin)), 3)

		feature1.remove(admin)
		self.assertEqual(len(layer1.getFeatures(admin)), 2)
		for feature in layer1.getFeatures(admin):
			self.assertIn(feature, (feature2, feature3))

	def test_updateFeature(self):
		admin = self._authenticate('eric')
		user = self._authenticate('george')

		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
		feature1 = Feature(name='Feature 1', description='Feature 1 description', creator=user, geometry='POINT(-0.1341533660888672 51.52459226699835)')
		layer1.addFeatures(admin, feature1)

		feature1.update(admin, name='Updated Feature1')
		self.assertEqual(feature1.name, 'Updated Feature1')

	def test_removeFeatureFromLayer(self):
		admin = self._authenticate('eric')
		user = self._authenticate('george')

		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
		feature1 = Feature(name='Feature 1', description='Feature 1 description', creator=user, geometry='POINT(-0.1341533660888672 51.52459226699835)')
		feature2 = Feature(name='Feature 2', description='Feature 2 description', creator=admin, geometry='POINT(-0.15192031860351562 51.5538605149062)')
		feature3 = Feature(name='Feature 3', description='Feature 3 description', creator=contributor, geometry='POINT(-0.0766897201538086 51.52388468468649)')
		layer1.addFeatures(admin, feature1, feature2, feature3)

		self.assertEqual(len(layer1.getFeatures(admin)), 3)

		layer1.removeFeatures(admin, feature1, feature2)
		self.assertEqual(len(layer1.getFeatures(admin)), 1)
		for feature in layer1.getFeatures(admin):
			self.assertEqual(feature, feature3)


	def test_addFeatureToLayer(self):
		admin = self._authenticate('eric')
		editor = self._authenticate('mehmet')
		contributor = self._authenticate('zindane')
		user = self._authenticate('george')

		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)

		editGroup = UserGroup(name='Edit Group', can_view=True, can_contribute=True, can_edit=True)
		editGroup.save()
		editGroup.addUsers(editor)

		contributeGroup = UserGroup(name='Edit Group', can_view=True, can_contribute=True)
		contributeGroup.save()
		contributeGroup.addUsers(contributor)

		layer1.addUserGroups(admin, editGroup, contributeGroup)

		feature1 = Feature(name='Feature 1', description='Feature 1 description', creator=user, geometry='POINT(-0.1341533660888672 51.52459226699835)')
		feature2 = Feature(name='Feature 2', description='Feature 2 description', creator=admin, geometry='POINT(-0.15192031860351562 51.5538605149062)')
		feature3 = Feature(name='Feature 3', description='Feature 3 description', creator=contributor, geometry='POINT(-0.0766897201538086 51.52388468468649)')

		with assertRaise(PermissionDenied):
			layer1.addFeatures(user, feature1)

		layer1.addFeatures(admin, feature1)
		layer1.addFeatures(contributor, feature2, feature3)

		for feature in layer1.getFeatures(admin):
			self.assertIn(feature, (feature1, feature2, feature3))