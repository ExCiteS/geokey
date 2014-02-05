from opencomap.tests.base import CommunityMapsTest

from django.core.exceptions import PermissionDenied
from opencomap.apps.backend import authorization
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.featuretype import FeatureType

class FeaturetypeAuthorizationTest(CommunityMapsTest):

	###########################################################################
	# GET FEATURE TYPES LIST
	###########################################################################

	def test_get_featuretype_list_with_creator(self):
		user = self._authenticate('eric')
		feature_types = authorization.featuretypes.get_list(user, self.private_project.id)
		self.assertEqual(len(feature_types), 3)

		for feature_type in feature_types:
			self.assertIn(feature_type, (self.active_feature_type, self.inactive_feature_type, self.private_feature_type))

	def test_get_featuretype_list_with_admin(self):
		user = self._authenticate('george')
		feature_types = authorization.featuretypes.get_list(user, self.private_project.id)
		self.assertEqual(len(feature_types), 3)

		for feature_type in feature_types:
			self.assertIn(feature_type, (self.active_feature_type, self.inactive_feature_type, self.private_feature_type))

	def test_get_featuretype_list_with_contributor(self):
		user = self._authenticate('diego')
		feature_types = authorization.featuretypes.get_list(user, self.private_project.id)
		self.assertEqual(len(feature_types), 2)

		for feature_type in feature_types:
			self.assertIn(feature_type, (self.active_feature_type, self.private_feature_type))

	def test_get_featuretype_list_with_viewgroup_member(self):
		user = self._authenticate('carlos')
		feature_types = authorization.featuretypes.get_list(user, self.private_project.id)
		self.assertEqual(len(feature_types), 2)

		for feature_type in feature_types:
			self.assertIn(feature_type, (self.active_feature_type, self.private_feature_type))

	def test_get_featuretype_list_with_non_member(self):
		user = self._authenticate('mehmet')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.get_list(user, self.private_project.id)

	###########################################################################
	# GET SINGLE FEATURE TYPES
	###########################################################################

	def test_get_single_featuretype_with_creator(self):
		user = self._authenticate('eric')
		featuretypes = self.private_project.featuretype_set.all()
		for feature_type in featuretypes:
			self.assertEqual(feature_type, authorization.featuretypes.get_single(user, self.private_project.id, feature_type.id))

	def test_get_single_featuretype_with_admin(self):
		user = self._authenticate('george')
		featuretypes = self.private_project.featuretype_set.all()
		for feature_type in featuretypes:
			self.assertEqual(feature_type, authorization.featuretypes.get_single(user, self.private_project.id, feature_type.id))

	def test_get_single_featuretype_with_contributor(self):
		user = self._authenticate('diego')
		featuretypes = self.private_project.featuretype_set.all()
		for feature_type in featuretypes:
			if feature_type.id == self.inactive_feature_type.id:
				with self.assertRaises(PermissionDenied):
					authorization.featuretypes.get_single(user, self.private_project.id, feature_type.id)
			else:
				self.assertEqual(feature_type, authorization.featuretypes.get_single(user, self.private_project.id, feature_type.id))

	def test_get_single_featuretype_with_view_member(self):
		user = self._authenticate('luis')
		featuretypes = self.private_project.featuretype_set.all()
		for feature_type in featuretypes:
			if feature_type.id == self.inactive_feature_type.id:
				with self.assertRaises(PermissionDenied):
					authorization.featuretypes.get_single(user, self.private_project.id, feature_type.id)
			else:
				self.assertEqual(feature_type, authorization.featuretypes.get_single(user, self.private_project.id, feature_type.id))

	def test_get_single_featuretype_with_non_member(self):
		user = self._authenticate('mehmet')
		featuretypes = self.private_project.featuretype_set.all()
		for feature_type in featuretypes:
			with self.assertRaises(PermissionDenied):
				authorization.featuretypes.get_single(user, self.private_project.id, feature_type.id)

	###########################################################################
	# UPDATE FEATURE TYPES
	###########################################################################

	def test_update_feature_type_with_admin(self):
		user = self._authenticate('eric')
		feature_type = authorization.featuretypes.update(user, self.private_project.id, self.active_feature_type.id, {"description": "new description"})
		self.assertEqual("new description", feature_type.description)

	def test_update_feature_type_with_contributor(self):
		user = self._authenticate('diego')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.update(user, self.private_project.id, self.active_feature_type.id, {"description": "new description"})
		
	def test_update_feature_type_with_view_member(self):
		user = self._authenticate('luis')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.update(user, self.private_project.id, self.active_feature_type.id, {"description": "new description"})

	def test_update_feature_type_with_non_member(self):
		user = self._authenticate('mehmet')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.update(user, self.private_project.id, self.active_feature_type.id, {"description": "new description"})

	###########################################################################
	# CREATE FEATURE TYPES
	###########################################################################

	def test_create_feature_type_with_admin(self):
		user = self._authenticate('eric')
		feature_type = authorization.featuretypes.create(user, self.private_project.id, {"name": "created", "description": "created description"})
		self.assertEqual(feature_type.name, "created")

	def test_create_feature_type_with_contributor(self):
		user = self._authenticate('diego')
		with self.assertRaises(PermissionDenied):
			feature_type = authorization.featuretypes.create(user, self.private_project.id, {"name": "created", "description": "created description"})

	def test_create_feature_type_with_view_member(self):
		user = self._authenticate('luis')
		with self.assertRaises(PermissionDenied):
			feature_type = authorization.featuretypes.create(user, self.private_project.id, {"name": "created", "description": "created description"})

	def test_create_feature_type_with_non_member(self):
		user = self._authenticate('mehmet')
		with self.assertRaises(PermissionDenied):
			feature_type = authorization.featuretypes.create(user, self.private_project.id, {"name": "created", "description": "created description"})

	###########################################################################
	# NON EXISTING
	###########################################################################

	def test_get_non_existing_project(self):
		user = self._authenticate('eric')
		with self.assertRaises(Project.DoesNotExist):
			authorization.featuretypes.get_single(user, 5643542342545452124, self.active_feature_type.id)

	def test_get_non_existing_feature_type(self):
		user = self._authenticate('eric')
		with self.assertRaises(FeatureType.DoesNotExist):
			authorization.featuretypes.get_single(user, self.private_project.id, 5643542342545452124)

	def test_create_on_non_existing_project(self):
		user = self._authenticate('eric')
		with self.assertRaises(Project.DoesNotExist):
			authorization.featuretypes.create(user, 5643542342545452124, {"name": "created", "description": "created description"})

	def test_update_non_existing_feature_type(self):
		user = self._authenticate('eric')
		with self.assertRaises(FeatureType.DoesNotExist):
			authorization.featuretypes.update(user, self.private_project.id, 5643542342545452124, {"description": "new description"})