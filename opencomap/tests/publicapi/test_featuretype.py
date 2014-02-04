from opencomap.tests.base import CommunityMapsTest

class FeatureTypeApiTest(CommunityMapsTest):
	def _get(self, user, project_id):
		url = '/api/projects/' + str(project_id) + '/featuretypes'
		return self.get_with_oauth(url, user)

	def test_featuretypesWithCreator(self):
		response = self._get('eric', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_feature_type))
		
		response = self._get('eric', self.private_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.private_feature_type))

		response = self._get('eric', self.inactive_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.inactive_feature_type))

		response = self._get('eric', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)

	def test_featuretypesWithAdmin(self):
		response = self._get('george', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_feature_type))
		
		response = self._get('george', self.private_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.private_feature_type))

		response = self._get('george', self.inactive_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.inactive_feature_type))

		response = self._get('george', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)

	def test_featuretypesWithContributor(self):
		response = self._get('diego', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_feature_type))
		
		response = self._get('diego', self.private_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.private_feature_type))

		response = self._get('diego', self.inactive_project.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('diego', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)

	def test_featuretypesWithNonMember(self):
		response = self._get('mehmet', self.public_project.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.objectSerializer.serialize(self.public_feature_type))
		
		response = self._get('mehmet', self.private_project.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('mehmet', self.inactive_project.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('mehmet', self.deleted_project.id)
		self.assertEqual(response.status_code, 404)