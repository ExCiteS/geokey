from ApiTest import ApiTest

class ProjectApiTest(ApiTest):
	def _get(self, user, project_id):
		url = '/api/projects'
		if project_id != None:
			url = url + '/' + str(project_id)
		
		return self.get_request(url, user)


	def test_projectsListWithCreator(self):
		response = self._get('eric', None)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		self.assertContains(response, self.objectSerializer.serialize(self.privateproject))
		self.assertContains(response, self.objectSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deletedproject))
		

	def test_projectsListWithAdmin(self):
		response = self._get('george', None)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		self.assertContains(response, self.objectSerializer.serialize(self.privateproject))
		self.assertContains(response, self.objectSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithViewGroupMember(self):
		response = self._get('peter', None)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		self.assertContains(response, self.objectSerializer.serialize(self.privateproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithContributor(self):
		response = self._get('diego', None)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		self.assertContains(response, self.objectSerializer.serialize(self.privateproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithNonMember(self):
		response = self._get('mehmet', None)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.privateproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.inactiveproject))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deletedproject))
		self.assertEqual(response.status_code, 200)

	def test_singleProjectsWithCreator(self):
		response = self._get('eric', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		
		response = self._get('eric', self.privateproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.privateproject))

		response = self._get('eric', self.inactiveproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.inactiveproject))

		response = self._get('eric', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)
		
	def test_singleProjectsWithAdmin(self):
		response = self._get('george', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		
		response = self._get('george', self.privateproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.privateproject))

		response = self._get('george', self.inactiveproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.inactiveproject))

		response = self._get('george', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)

	def test_singleProjectsWithContributor(self):
		response = self._get('diego', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		
		response = self._get('diego', self.privateproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.privateproject))

		response = self._get('diego', self.inactiveproject.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('diego', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)

	def test_singleProjectsWithViewgroupMemberg(self):
		response = self._get('peter', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		
		response = self._get('peter', self.privateproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.privateproject))

		response = self._get('peter', self.inactiveproject.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('peter', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)

	def test_singleProjectsWithNonMember(self):
		response = self._get('mehmet', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.publicproject))
		
		response = self._get('mehmet', self.privateproject.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('mehmet', self.inactiveproject.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('mehmet', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)
