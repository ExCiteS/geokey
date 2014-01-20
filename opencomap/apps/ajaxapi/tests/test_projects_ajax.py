from AjaxTest import AjaxTest
from opencomap.libs.serializers import ObjectSerializer
from opencomap.apps.backend.models.choice import STATUS_TYPES

class ProjectAjaxTest(AjaxTest):

	# ###################################
	# REMOVE USERS FROM GROUPS
	# ###################################
	
	def test_removeUsersWithWrongMethod(self):
		response = self.get('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/10', 'eric')
		self.assertEqual(response.status_code, 405)

	def test_removeNotExistingUser(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/10000', 'eric')
		self.assertEqual(response.status_code, 404)

	def test_removeWrongUser(self):
		userToRemove = self._authenticate('carlos')
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), 'eric')
		self.assertEqual(response.status_code, 404)

	def test_removeUsersWithCreator(self):
		userToRemove = self._authenticate('george')
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, ObjectSerializer().serialize([userToRemove]))

	def test_removeUsersWithAdmin(self):
		userToRemove = self._authenticate('george')
		self.project.admins.addUsers(self._authenticate('carlos'))

		response = self.delete('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), 'carlos')
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, ObjectSerializer().serialize([userToRemove]))

	def test_removeUsersWithContributor(self):
		userToRemove = self._authenticate('george')
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), 'diego')
		self.assertEqual(response.status_code, 401)

	def test_removeUsersWithNonMember(self):
		userToRemove = self._authenticate('george')
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id) + '/users/' + str(userToRemove.id), 'mehmet')
		self.assertEqual(response.status_code, 401)

	# ###################################
	# ADD USERS TO GROUPS
	# ###################################
	 
	def test_addUsersWrongUserGroup(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.referenceGroup.id), {'userId': 10000}, 'eric')
		self.assertEqual(response.status_code, 404)

	def test_addUsersWithWrongMethod(self):
		response = self.post('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), {'userId': 10}, 'eric')
		self.assertEqual(response.status_code, 405)

	def test_addNotExistingUser(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), {'userId': 10000}, 'eric')
		self.assertEqual(response.status_code, 400)
	
	def test_addUsersWithCreator(self):
		userToAdd = self._authenticate('carlos')

		response = self.put('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), {'userId': userToAdd.id}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, ObjectSerializer().serialize([userToAdd]))

	def test_addUsersWithCreator(self):
		userToAdd = self._authenticate('carlos')
		response = self.put('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), {'userId': userToAdd.id}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, ObjectSerializer().serialize([userToAdd]))

	def test_addUsersWithContributor(self):
		userToAdd = self._authenticate('carlos')

		response = self.put('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), {'userId': userToAdd.id}, 'diego')
		self.assertEqual(response.status_code, 401)

	def test_addUsersWithNonMember(self):
		userToAdd = self._authenticate('carlos')
		response = self.put('/ajax/projects/' + str(self.project.id) + '/usergroups/' + str(self.project.admins.id), {'userId': userToAdd.id}, 'mehmet')

		self.assertEqual(response.status_code, 401)

	# ###################################
	# UPDATE STATUS
	# ###################################
	
	def test_updateStatusWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'status': STATUS_TYPES['INACTIVE']}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"status": ' + str(STATUS_TYPES['INACTIVE']))
		

	def test_updateStatusWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'status': STATUS_TYPES['ACTIVE']}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"isprivate": true')

	def test_updateStatusWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'status': STATUS_TYPES['ACTIVE']}, 'diego')
		self.assertEqual(response.status_code, 401)

	def test_updateStatusWithNonMember(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'status': STATUS_TYPES['ACTIVE']}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	# ###################################
	# UPDATE PRIVATE
	# ###################################
	
	def test_updatePrivateWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'isprivate': False}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"isprivate": false')
		

	def test_updatePrivateWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'isprivate': True}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"isprivate": true')


	def test_updatePrivateWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'isprivate': True}, 'diego')
		self.assertEqual(response.status_code, 401)

	def test_updatePrivateWithNonMember(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'isprivate': True}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	# ###################################
	# UPDATE DESCRIPTION
	# ###################################

	def test_updateNotExistingProject(self):
		response = self.put('/ajax/projects/10000', {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 404)

	def test_updateDescriptionWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def test_updateDescriptionWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'description': 'newer description'}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "newer description"')

	def test_updateDescriptionWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'description': 'new description'}, 'diego')
		self.assertEqual(response.status_code, 401)

	def test_updateDescriptionWithNonMember(self):
		response = self.put('/ajax/projects/' + str(self.project.id), {'description': 'new description'}, 'mehmet')
		self.assertEqual(response.status_code, 401)


	# ###################################
	# DELETE PROJECT
	# ###################################

	def test_deleteNotExistingProject(self):
		response = self.delete('/ajax/projects/10000', 'eric')
		self.assertEqual(response.status_code, 404)

	def test_deleteProjectWithCreator(self):
		response = self.delete('/ajax/projects/' + str(self.project.id), 'eric')
		self.assertEqual(response.status_code, 200)

	def test_deleteProjectWithAdmin(self):
		response = self.delete('/ajax/projects/' + str(self.project.id), 'george')
		self.assertEqual(response.status_code, 200)

	def test_deleteProjectWithContributor(self):
		response = self.delete('/ajax/projects/' + str(self.project.id), 'diego')
		self.assertEqual(response.status_code, 401)

	def test_deleteProjectWithNonMember(self):
		response = self.delete('/ajax/projects/' + str(self.project.id), 'mehmet')
		self.assertEqual(response.status_code, 401)