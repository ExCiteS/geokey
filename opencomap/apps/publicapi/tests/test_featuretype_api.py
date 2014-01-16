from ApiTest import ApiTest

class FeaturetypeApiTest(ApiTest):
	def _get(self, user, project_id):
		url = '/api/projects/' + str(project_id) + '/featuretypes'
		return self.get_request(url, user)

	def test_featuretypesWithCreator(self):
		response = self._get('eric', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicFeatureType))
		
		response = self._get('eric', self.privateproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateFeatureType))

		response = self._get('eric', self.inactiveproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveFeatureType))

		response = self._get('eric', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)

	def test_featuretypesWithAdmin(self):
		response = self._get('george', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicFeatureType))
		
		response = self._get('george', self.privateproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateFeatureType))

		response = self._get('george', self.inactiveproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.inactiveFeatureType))

		response = self._get('george', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)


	def test_featuretypesWithContributor(self):
		response = self._get('diego', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicFeatureType))
		
		response = self._get('diego', self.privateproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.privateFeatureType))

		response = self._get('diego', self.inactiveproject.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('diego', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)

	def test_featuretypesWithNonMember(self):
		response = self._get('mehmet', self.publicproject.id)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.singleSerializer.serialize(self.publicFeatureType))
		
		response = self._get('mehmet', self.privateproject.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('mehmet', self.inactiveproject.id)
		self.assertEqual(response.status_code, 401)

		response = self._get('mehmet', self.deletedproject.id)
		self.assertEqual(response.status_code, 404)