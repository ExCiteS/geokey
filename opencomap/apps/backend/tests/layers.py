from django.test import TestCase

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied

from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.projects import ProjectFactory
from opencomap.apps.backend.models.layers import Layer
from opencomap.apps.backend.models.layers import LayerFactory

class LayersTest(TestCase):
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

	def test_Permissions(self):
		admin = self._authenticate('eric')
		user = self._authenticate('george')

		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
		project1 = ProjectFactory('Test Project 1', 'Lorem ipsum dolor sit amet', admin)

		self.assertTrue(layer1.userCanView(admin))
		self.assertTrue(layer1.userCanEdit(admin))
		self.assertTrue(layer1.userCanAdmin(admin))
		self.assertTrue(layer1.userCanContribute(admin))

		self.assertTrue(layer1.userCanView(user))
		self.assertFalse(layer1.userCanEdit(user))
		self.assertFalse(layer1.userCanAdmin(user))
		self.assertFalse(layer1.userCanContribute(user))

	def test_assignToProject(self):
		admin = self._authenticate('eric')

		layer1 = LayerFactory('Test Layer 1', 'Lorem ipsum dolor sit amet', admin)
		layer2 = LayerFactory('Test Layer 2', 'Lorem ipsum dolor sit amet', admin)
		layer3 = LayerFactory('Test Layer 3', 'Lorem ipsum dolor sit amet', admin)
		project1 = ProjectFactory('Test Project 1', 'Lorem ipsum dolor sit amet', admin)

		project1.addLayers(admin, layer1)
		self.assertEqual(len(Layer.objects.filter(projects__id__exact=project1.id)), 1)
		self.assertIn(project1, Layer.objects.filter(projects__id__exact=project1.id)[0].projects.all())

		project1.addLayers(admin, layer2, layer3)
		self.assertEqual(len(Layer.objects.filter(projects__id__exact=project1.id)), 3)
		for layer in Layer.objects.filter(projects__id__exact=project1.id):
			self.assertIn(layer, (layer1, layer2, layer3))

	def test_createLayer(self):
		user = self._authenticate('eric')

		layer = LayerFactory('Test Layer', 'Lorem ipsum dolor sit amet', user)
		self.assertEqual(layer.creator, user)

		for group in layer.usergroups.all():
			self.assertIn(group.name, ('Admin', 'General public'))
			if (group.name == 'Admin'):
				self.assertEqual(len(group.users.all()), 1)
				self.assertEqual(group.users.all()[0], user)