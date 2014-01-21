from AjaxTest import AjaxTest
from opencomap.apps.backend.models.choice import STATUS_TYPES
import json

class FeatureTypeAjaxTest(AjaxTest):
	def test_updateDescriptionWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def test_updateDescriptionWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'newer description'}, 'george')
		self.assertContains(response, '"description": "newer description"')
		self.assertEqual(response.status_code, 200)

	def test_updateDescriptionWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'new description'}, 'diego')
		self.assertEqual(response.status_code, 401)

	def test_updateDescriptionWithNonMember(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'new description'}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	def test_updateDescriptionWrongMethod(self):
		response = self.post('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'new description'}, 'diego')
		self.assertEqual(response.status_code, 405)

	def test_updateDescriptionNonExistingFeaturetype(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/684640654540', {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 404)

	def test_updateFalseStatus(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'status': 656045}, 'eric')
		self.assertEqual(response.status_code, 400)

	def test_updateCorrectStatus(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'status': STATUS_TYPES['INACTIVE']}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"status": ' + str(STATUS_TYPES['INACTIVE']))

	def testUpdateFieldWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.field.id), {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def testUpdateFieldWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.field.id), {'description': 'newer description'}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "newer description"')

	def testUpdateFieldWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.field.id), {'description': 'newer description'}, 'diego')
		self.assertEqual(response.status_code, 401)

	def testUpdateFieldWithNonMember(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.field.id), {'description': 'newer description'}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	def test_updateFieldFalseStatus(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.field.id), {'status': 656045}, 'eric')
		self.assertEqual(response.status_code, 400)

	def test_updateFieldCorrectStatus(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.field.id), {'status': STATUS_TYPES['INACTIVE']}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"status": ' + str(STATUS_TYPES['INACTIVE']))

	def test_updateFieldNonExistingFeaturetype(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/684640654540/fields/' + str(self.field.id), {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 404)

	def test_updateFieldNonExistingField(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/54545454415484', {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 404)

	def test_addLookupValueWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.lookupfield.id) + '/lookupvalues', {'name': 'Piggy'}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"name": "Piggy"')

	def test_addLookupValueWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.lookupfield.id) + '/lookupvalues', {'name': 'Kermit'}, 'george')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"name": "Kermit"')

	def test_addLookupValueWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.lookupfield.id) + '/lookupvalues', {'name': 'Kermit'}, 'diego')
		self.assertEqual(response.status_code, 401)

	def test_addLookupValueWithNonMember(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.lookupfield.id) + '/lookupvalues', {'name': 'Kermit'}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	def test_addLookupValueOnTextField(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.field.id) + '/lookupvalues', {'name': 'Kermit'}, 'eric')
		self.assertEqual(response.status_code, 404)

	def test_addLookupValueThatExisistButIsInactive(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.lookupfield.id) + '/lookupvalues', {'id': self.lookupvalue.id, 'name': 'Kermit'}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"name": "Gonzo"')
		self.assertNotContains(response, '"status": 1')

	def test_removeLookupValue(self):
		self.lookupvalue.status = 0
		self.lookupvalue.save()
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.lookupfield.id) + '/lookupvalues/' + str(self.lookupvalue.id), 'eric')
		self.assertEqual(response.status_code, 200)
		for lookup in json.loads(response.content).get('field').get('lookupvalues'):
			if lookup.get('name') == 'Gonzo':
				self.assertEqual(lookup.get('status'), 1)

	def test_removeLookupValueThatDoesNotExist(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id) + '/fields/' + str(self.lookupfield.id) + '/lookupvalues/468413515121', 'eric')
		self.assertEqual(response.status_code, 404)
