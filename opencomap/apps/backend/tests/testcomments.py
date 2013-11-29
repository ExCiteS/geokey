from django.test import TestCase
from opencomap.apps.backend.models.factory import Factory
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.feature import Feature
from opencomap.apps.backend.models.feature import Observation
from opencomap.apps.backend.models.featuretype import FeatureType
from opencomap.apps.backend.models.featuretype import TextField
from opencomap.apps.backend.models.featuretype import NumericField
from opencomap.apps.backend.models.featuretype import TrueFalseField
from opencomap.apps.backend.models.featuretype import LookupField
from opencomap.apps.backend.models.featuretype import LookupValue
from opencomap.apps.backend.models.comment import FeatureComment
from opencomap.apps.backend.models.comment import ObservationComment
from opencomap.apps.backend.models.choice import STATUS_TYPES

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError



class CommentsTest(TestCase):
	class Meta: 
		app_label = 'backend'

	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def setUp(self):
		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('zinedine', 'zinedine@zidane.fr', 'zinedine123', first_name='Zinedine', last_name='Zidane').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diego123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('carlos', 'carlos@valderama.co', 'carlos123', first_name='Carlos', last_name='Valderama').save()

		admin = self._authenticate('eric')

		# Creating Project
		project = Factory().createProject('First Project', 'First Project description', admin)
		
		# Creating FeatureType
		featureType = FeatureType(name='Test Feature Type')
		project.addFeatureType(featureType)
		
		# Creating example field types for each features
		textField = TextField(name='Text', description='Text field description')
		featureType.addField(textField)
		
		
		project.addFeature(Feature(name='Example Feature 1', description='Example feature description', featuretype=featureType, creator=admin, geometry='POINT(-0.15003204345703125 51.55615526777012)'))
		project.addFeature(Feature(name='Example Feature 2', description='Example feature description', featuretype=featureType, creator=admin, geometry='POINT(-0.1544952392578125 51.53074643430678)'))

		for feature in project.getFeatures():
			for i in range(0, 5):
				user = self._authenticate('mehmet')
				feature.addObservation(Observation(creator=admin, data={'Text': 'Textfield val'}))

	def test_addCommentToFeature(self):
		users = ['george', 'mehmet', 'zinedine', 'diego', 'carlos']
		project = Project.objects.all()[0]

		for feature in project.getFeatures():
			for i in range(0, 5):
				user = self._authenticate(users[i])
				feature.addComment(FeatureComment(text=feature.name + 'Comment #' + str(i), creator=user))

		for feature in project.getFeatures():
			self.assertEqual(len(feature.getComments()), 5)
			for comment in feature.getComments():
				self.assertTrue(comment.text.startswith(feature.name))
				
	def test_deleteCommentFeature(self):
		users = ['george', 'mehmet', 'zinedine', 'diego', 'carlos']
		project = Project.objects.all()[0]

		for feature in project.getFeatures():
			for i in range(0, 5):
				user = self._authenticate(users[i])
				feature.addComment(FeatureComment(text=feature.name + 'Comment #' + str(i), creator=user))

		for feature in project.getFeatures():
			deleted = 0
			self.assertEqual(len(feature.getComments()), 5)
			if feature.name == 'Example Feature 1':
				for comment in feature.getComments():
					if deleted < 2:
						comment.delete()
						self.assertEqual(comment.status, STATUS_TYPES['DELETED'])
						deleted = deleted + 1

		for feature in project.getFeatures():
			if feature.name == 'Example Feature 1':
				self.assertEqual(len(feature.getComments()), 3)
			else:
				self.assertEqual(len(feature.getComments()), 5)

			for comment in feature.getComments():
				self.assertTrue(comment.text.startswith(feature.name))

	def test_removeCommentFromFeature(self):
		users = ['george', 'mehmet', 'zinedine', 'diego', 'carlos']
		project = Project.objects.all()[0]

		for feature in project.getFeatures():
			for i in range(0, 5):
				user = self._authenticate(users[i])
				feature.addComment(FeatureComment(text=feature.name + 'Comment #' + str(i), creator=user))

		for feature in project.getFeatures():
			deleted = 0
			self.assertEqual(len(feature.getComments()), 5)
			if feature.name == 'Example Feature 1':
				for comment in feature.getComments():
					if deleted < 2:
						feature.removeComments(comment)
						self.assertEqual(comment.status, STATUS_TYPES['DELETED'])
						deleted = deleted + 1

		for feature in project.getFeatures():
			if feature.name == 'Example Feature 1':
				self.assertEqual(len(feature.getComments()), 3)
			else:
				self.assertEqual(len(feature.getComments()), 5)

			for comment in feature.getComments():
				self.assertTrue(comment.text.startswith(feature.name))

	def test_addCommentToObservation(self):
		users = ['george', 'mehmet', 'zinedine', 'diego', 'carlos']
		project = Project.objects.all()[0]

		for feature in project.getFeatures():
			for observation in feature.getObservations():
				for i in range(0, 5):
					user = self._authenticate(users[i])
					observation.addComment(ObservationComment(text=feature.name + 'Comment #' + str(i), creator=user))

		for feature in project.getFeatures():
			for observation in feature.getObservations():
				self.assertEqual(len(observation.getComments()), 5)
				for comment in observation.getComments():
					self.assertTrue(comment.text.startswith(feature.name))

	# def test_commendOnComments(self):

	# def test_deleteCommentObservation(self):
	# def test_removeCommentFromObservation(self):
