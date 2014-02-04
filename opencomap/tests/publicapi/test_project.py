from opencomap.tests.base import CommunityMapsTest

class ProjectApiTest(CommunityMapsTest):
	def _get(self, user, project_id):
		url = '/api/projects'
		if project_id != None:
			url = url + '/' + str(project_id)
		
		return self.get_with_oauth(url, user)


	def test_projectsListWithCreator(self):
		response = self._get('eric', None)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		self.assertContains(response, self.objectSerializer.serialize(self.private_project))
		self.assertContains(response, self.objectSerializer.serialize(self.inactive_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deleted_project))

	def test_projectsListWithAdmin(self):
		response = self._get('george', None)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		self.assertContains(response, self.objectSerializer.serialize(self.private_project))
		self.assertContains(response, self.objectSerializer.serialize(self.inactive_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deleted_project))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithViewGroupMember(self):
		response = self._get('peter', None)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		self.assertContains(response, self.objectSerializer.serialize(self.private_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.inactive_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deleted_project))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithContributor(self):
		response = self._get('diego', None)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		self.assertContains(response, self.objectSerializer.serialize(self.private_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.inactive_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deleted_project))
		self.assertEqual(response.status_code, 200)

	def test_projectsListWithNonMember(self):
		response = self._get('mehmet', None)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.private_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.inactive_project))
		self.assertNotContains(response, self.objectSerializer.serialize(self.deleted_project))
		self.assertEqual(response.status_code, 200)

	def test_singleProjectsWithCreator(self):
		response = self._get('eric', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		
		response = self._get('eric', self.private_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.private_project))

		response = self._get('eric', self.inactive_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.inactive_project))

		response = self._get('eric', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)
		
	def test_singleProjectsWithAdmin(self):
		response = self._get('george', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		
		response = self._get('george', self.private_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.private_project))

		response = self._get('george', self.inactive_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.inactive_project))

		response = self._get('george', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)

	def test_singleProjectsWithContributor(self):
		response = self._get('diego', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		
		response = self._get('diego', self.private_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.private_project))

		response = self._get('diego', self.inactive_project.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('diego', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)

	def test_singleProjectsWithViewgroupMemberg(self):
		response = self._get('peter', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		
		response = self._get('peter', self.private_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.private_project))

		response = self._get('peter', self.inactive_project.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('peter', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)

	def test_singleProjectsWithNonMember(self):
		response = self._get('mehmet', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_project))
		
		response = self._get('mehmet', self.private_project.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('mehmet', self.inactive_project.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('mehmet', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)
