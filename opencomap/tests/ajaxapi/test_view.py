from opencomap.tests.base import CommunityMapsTest
from opencomap.apps.backend.models.choice import STATUS_TYPES

class ViewAjaxTest(CommunityMapsTest):
	def testViewWithWrongMethod(self):
		response = self.get('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), 'eric')
		self.assertEqual(response.status_code, 405)

	# ###################################
	# UPDATE VIEW
	# ###################################

	def testUpdateViewWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def testUpdateViewWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), {'description': 'new description'}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def testUpdateViewWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), {'description': 'new description'}, 'diego')
		self.assertEqual(response.status_code, 401)

	def testUpdateViewWithNonMember(self):
		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), {'description': 'new description'}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	def testUpdateNonExisitingView(self):
		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/684564521545121', {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 404)

	# ###################################
	# DELETE VIEW
	# ###################################

	def testDeleteViewWithCreator(self):
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '{"success": "The view has been deleted."}')

	def testDeleteViewWithAdmin(self):
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '{"success": "The view has been deleted."}')

	def testDeleteViewWithContributor(self):
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), 'diego')
		self.assertEqual(response.status_code, 401)

	def testDeleteViewWithNonMenmber(self):
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id), 'mehmet')
		self.assertEqual(response.status_code, 401)

	def testDeleteNonExisitingView(self):
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/684564521545121', 'eric')
		self.assertEqual(response.status_code, 404)

	# ###################################
	# ADD USER TO GROUP
	# ###################################

	def test_addUsersWithCreator(self):
		userToAdd = self._authenticate('carlos')

		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users', {'userId': userToAdd.id}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(userToAdd))

	def test_addUsersWithAdmin(self):
		userToAdd = self._authenticate('carlos')

		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users', {'userId': userToAdd.id}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(userToAdd))

	def test_addUsersWithContributor(self):
		userToAdd = self._authenticate('carlos')

		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users', {'userId': userToAdd.id}, 'diego')
		self.assertEqual(response.status_code, 401)

	def test_addUsersWithNonMember(self):
		userToAdd = self._authenticate('carlos')

		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users', {'userId': userToAdd.id}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	def test_addUserThatDoesNotExist(self):
		response = self.put('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users', {'userId': 56454521874545}, 'eric')
		self.assertEqual(response.status_code, 400)

	def test_addUserWrongMethod(self):
		response = self.get('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users', 'eric')
		self.assertEqual(response.status_code, 405)

	# ###################################
	# REMOVE USER FROM GROUP
	# ###################################

	def test_removeUsersWithCreator(self):
		userToRemove = self._authenticate('peter')
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users/' + str(userToRemove.id), 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, self.objectSerializer.serialize(userToRemove))

	def test_removeUsersWithAdmin(self):
		userToRemove = self._authenticate('peter')
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users/' + str(userToRemove.id), 'george')
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, self.objectSerializer.serialize(userToRemove))

	def test_removeUsersWithContributor(self):
		userToRemove = self._authenticate('peter')
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users/' + str(userToRemove.id), 'diego')
		self.assertEqual(response.status_code, 401)

	def test_removeUsersWithNonMember(self):
		userToRemove = self._authenticate('peter')
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users/' + str(userToRemove.id), 'mehmet')
		self.assertEqual(response.status_code, 401)

	def test_removeUsersThatDoesNotExist(self):
		userToRemove = self._authenticate('peter')
		response = self.delete('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users/5854545784847845', 'eric')
		self.assertEqual(response.status_code, 404)

	def test_removeUsersWrongMethod(self):
		userToRemove = self._authenticate('peter')
		response = self.get('/ajax/projects/' + str(self.private_project.id) + '/views/' + str(self.active_view.id) + '/usergroups/' + str(self.active_view_group.id) + '/users/5854545784847845', 'mehmet')
		self.assertEqual(response.status_code, 405)