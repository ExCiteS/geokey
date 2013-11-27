from django.test import TestCase
from opencomap.apps.backend.models.factory import Factory
from opencomap.apps.backend.models.projects import Project
from opencomap.apps.backend.models.features import Feature
from opencomap.apps.backend.models.features import Observation
from opencomap.apps.backend.models.fields import FeatureType
from opencomap.apps.backend.models.fields import TextField
from opencomap.apps.backend.models.fields import NumericField
from opencomap.apps.backend.models.fields import TrueFalseField
from opencomap.apps.backend.models.fields import LookupField
from opencomap.apps.backend.models.fields import LookupValue
from opencomap.apps.backend.models.choices import STATUS_TYPES

from django.contrib.auth.models import User
from django.contrib.auth import authenticate



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
		project = Factory().createProject('First Project', 'First Project description', admin)
		
		# Creating FeatureType
		featureType = FeatureType(name='Test Feature Type', project=project)
		featureType.save()
		
		# Creating example field types for each features
		# textField = TextField(name='Text field', description='Text field description', featuretype=featureType)
		# textField.save()
		# numericField = NumericField(name='Numeric field', description='Numeric field description', required=True, featuretype=featureType)
		# numericField.save()
		# dateField = DateTimeField(name='Date field', description='Date field description', featuretype=featureType)
		# dateField.save()
		# boolField = TrueFalseField(name='Bool field', description='Bool field description', featuretype=featureType)
		# boolField.save()
		# lookupField = LookupField(name='Lookup field', description='Lookup field description', featuretype=featureType)
		# lookupField.save()
		# lookupField.addLookupValues('Value 1', 'Value 2', 'Value 3')

		# f = Feature(name='Example Feature', description='Example feature description', featuretype=featureType, creator=admin, geometry='POINT(-0.15003204345703125 51.55615526777012)')
		# f.save()
		# project.addFeatures(f)

	# def test_validateText(self):
	# 	admin = self._authenticate('eric')
	# 	project = Project.objects.all()[0]
	# 	featureType = project.getFeatureTypes()[0]

	# 	textField = TextField(name='Text field', description='Text field description', featuretype=featureType)
	# 	textField.save()

	# 	f = Feature(name='Example Feature', description='Example feature description', featuretype=featureType, creator=admin, geometry='POINT(-0.15003204345703125 51.55615526777012)')
	# 	f.save()
	# 	project.addFeatures(f)

	# 	