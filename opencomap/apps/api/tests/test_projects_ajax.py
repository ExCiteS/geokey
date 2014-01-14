from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import json
from opencomap.apps.api.serializers import SingleSerializer

import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.choice import STATUS_TYPES

class ProjectAjaxTest(TestCase):
	def _authenticate(self, name):
		return authenticate(username=name, password=name + '123')

	def setUp(self):
		User.objects.create_user('eric', 'eric@cantona.fr', 'eric123', first_name='Eric', last_name='Cantona').save()
		User.objects.create_user('george', 'eric@best.uk', 'george123', first_name='George', last_name='Best').save()
		User.objects.create_user('diego', 'diego@maradonna.ar', 'diego123', first_name='Diego', last_name='Maradonna').save()
		User.objects.create_user('mehmet', 'mehmet@scholl.de', 'mehmet123', first_name='Mehmet', last_name='Scholl').save()
		User.objects.create_user('carlos', 'carlos@valderama.de', 'carlos123', first_name='carlos', last_name='valderama').save()

		eric = self._authenticate('eric')
		george = self._authenticate('george')
		diego = self._authenticate('diego')
		carlos = self._authenticate('carlos')

		self.project = Factory.createProject('Project', 'Test description', eric, isprivate=True)
		self.project.admins.addUsers(george)
		self.project.contributors.addUsers(diego)
		self.project.save()

		testProject = Factory.createProject('Test Project', 'Test description', carlos)
		self.referenceGroup = testProject.admins

		self.client = Client()

	# ###################################
	# REMOVE USERS FROM GROUPS
	# ###################################
	
	def test_removeUsersWithWrongMethod(self):
		self.client.login(username='eric', password='eric123')
		response = self.client.post('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/10', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 405)

	def test_removeNotExistingUser(self):
		self.client.login(username='eric', password='eric123')
		response = self.client.delete('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/10000', HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 404)

	def test_removeNotWrongUser(self):
		userToRemove = self._authenticate('carlos')
		self.client.login(username='eric', password='eric123')
		response = self.client.delete('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 404)

	def test_removeUsersWithCreator(self):
		userToRemove = self._authenticate('george')

		self.client.login(username='eric', password='eric123')
		response = self.client.delete('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		serializer = SingleSerializer()
		self.assertNotContains(response, serializer.serialize(userToRemove))

	def test_removeUsersWithAdmin(self):
		userToRemove = self._authenticate('george')
		self.project.admins.addUsers(self._authenticate('carlos'))

		self.client.login(username='carlos', password='carlos123')
		response = self.client.delete('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		serializer = SingleSerializer()
		self.assertNotContains(response, serializer.serialize(userToRemove))

	def test_removeUsersWithContributor(self):
		userToRemove = self._authenticate('george')

		self.client.login(username='diego', password='diego123')
		response = self.client.delete('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	def test_removeUsersWithNonMember(self):
		userToRemove = self._authenticate('george')

		self.client.login(username='mehmet', password='mehmet123')
		response = self.client.delete('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	# ###################################
	# ADD USERS TO GROUPS
	# ###################################
	 
	def test_addUsersWrongUserGroup(self):
		self.client.login(username='eric', password='eric123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.referenceGroup.id), json.dumps({'userId': 10000}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 404)

	def test_addUsersWithWrongMethod(self):
		self.client.login(username='eric', password='eric123')
		response = self.client.post('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), json.dumps({'userId': 10}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 405)

	def test_addNotExistingUser(self):
		self.client.login(username='eric', password='eric123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), json.dumps({'userId': 10000}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')

		self.assertEqual(response.status_code, 400)
	
	def test_addUsersWithCreator(self):
		userToAdd = self._authenticate('carlos')

		self.client.login(username='eric', password='eric123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), json.dumps({'userId': userToAdd.id}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		serializer = SingleSerializer()
		self.assertContains(response, serializer.serialize(userToAdd))

	def test_addUsersWithCreator(self):
		userToAdd = self._authenticate('carlos')

		self.client.login(username='george', password='george123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), json.dumps({'userId': userToAdd.id}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		serializer = SingleSerializer()
		self.assertContains(response, serializer.serialize(userToAdd))

	def test_addUsersWithContributor(self):
		userToAdd = self._authenticate('carlos')

		self.client.login(username='diego', password='diego123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), json.dumps({'userId': userToAdd.id}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	def test_addUsersWithNonMember(self):
		userToAdd = self._authenticate('carlos')

		self.client.login(username='mehmet', password='mehmet123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), json.dumps({'userId': userToAdd.id}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	# ###################################
	# UPDATE STATUS
	# ###################################
	
	def test_updateStatusWithCreator(self):
		self.client.login(username='eric', password='eric123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'status': STATUS_TYPES['INACTIVE']}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"status": ' + str(STATUS_TYPES['INACTIVE']))
		

	def test_updateStatusWithAdmin(self):
		self.client.login(username='george', password='george123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'status': STATUS_TYPES['ACTIVE']}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"isprivate": true')


	def test_updateStatusWithContributor(self):
		self.client.login(username='diego', password='diego123')

		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'status': STATUS_TYPES['ACTIVE']}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	def test_updateStatusWithNonMember(self):
		self.client.login(username='mehmet', password='mehmet123')

		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'status': STATUS_TYPES['ACTIVE']}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	# ###################################
	# UPDATE PRIVATE
	# ###################################
	
	def test_updatePrivateWithCreator(self):
		self.client.login(username='eric', password='eric123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'isprivate': False}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"isprivate": false')
		

	def test_updatePrivateWithAdmin(self):
		self.client.login(username='george', password='george123')
		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({"isprivate": True}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"isprivate": true')


	def test_updateDescriptionWithContributor(self):
		self.client.login(username='diego', password='diego123')

		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({"isprivate": True}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	def test_updateDescriptionWithNonMember(self):
		self.client.login(username='mehmet', password='mehmet123')

		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({"isprivate": True}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	# ###################################
	# UPDATE DESCRIPTION
	# ###################################

	def test_updateNotExistingProject(self):
		self.client.login(username='eric', password='eric123')

		response = self.client.put('/api/ajax/project/10000', json.dumps({'description': 'new description'}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 404)

	def test_updateDescriptionWithCreator(self):
		self.client.login(username='eric', password='eric123')

		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'description': 'new description'}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def test_updateDescriptionWithAdmin(self):
		self.client.login(username='george', password='george123')

		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'description': 'newer description'}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "newer description"')

	def test_updateDescriptionWithContributor(self):
		self.client.login(username='diego', password='diego123')

		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'description': 'new description'}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	def test_updateDescriptionWithNonMember(self):
		self.client.login(username='mehmet', password='mehmet123')

		response = self.client.put('/api/ajax/project/' + str(self.project.id), json.dumps({'description': 'new description'}), HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
		self.assertEqual(response.status_code, 401)


	# ###################################
	# DELETE PROJECT
	# ###################################

	def test_deleteNotExistingProject(self):
		self.client.login(username='eric', password='eric123')

		response = self.client.delete('/api/ajax/project/10000', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 404)

	def test_deleteProjectWithCreator(self):
		self.client.login(username='eric', password='eric123')

		response = self.client.delete('/api/ajax/project/' + str(self.project.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)

	def test_deleteProjectWithAdmin(self):
		self.client.login(username='george', password='george123')

		response = self.client.delete('/api/ajax/project/' + str(self.project.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)

	def test_deleteProjectWithContributor(self):
		self.client.login(username='diego', password='diego123')

		response = self.client.delete('/api/ajax/project/' + str(self.project.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 401)

	def test_deleteProjectWithNonMember(self):
		self.client.login(username='mehmet', password='mehmet123')

		response = self.client.delete('/api/ajax/project/' + str(self.project.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 401)