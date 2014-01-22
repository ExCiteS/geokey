from AjaxTest import AjaxTest

class ViewAjaxTest(AjaxTest):

	def testViewWithWrongMethod(self):
		response = self.get('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), 'eric')
		self.assertEqual(response.status_code, 405)

	# ###################################
	# UPDATE VIEW
	# ###################################

	def testUpdateViewWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def testUpdateViewWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), {'description': 'new description'}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def testUpdateViewWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), {'description': 'new description'}, 'diego')
		self.assertEqual(response.status_code, 401)

	def testUpdateViewWithNonMemberg(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), {'description': 'new description'}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	def testUpdateNonExisitingView(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/views/684564521545121', {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 404)

	# ###################################
	# DELETE VIEW
	# ###################################

	def testDeleteViewWithCreator(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '{"success": "The view has been deleted."}')

	def testDeleteViewWithAdmin(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '{"success": "The view has been deleted."}')

	def testDeleteViewWithContributor(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), 'diego')
		self.assertEqual(response.status_code, 401)

	def testDeleteViewWithNonMenmber(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/views/' + str(self.project.getViews()[0].id), 'mehmet')
		self.assertEqual(response.status_code, 401)

	def testDeleteNonExisitingView(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/views/684564521545121', 'eric')
		self.assertEqual(response.status_code, 404)