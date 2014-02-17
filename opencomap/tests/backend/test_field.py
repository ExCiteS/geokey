from opencomap.tests.base import CommunityMapsTest

from django.core.exceptions import PermissionDenied
from opencomap.apps.backend import authorization

class FieldAuthorizationTest(CommunityMapsTest):
	###########################################################################
	# GET FIELD LIST
	###########################################################################
	#
	def test_get_field_list_with_admin(self):
		user = self._authenticate('george')
		fields = authorization.featuretypes.get_list_field(user, self.private_project.id, self.active_feature_type.id)
		self.assertEqual(len(fields), 3)

		for field in fields:
			self.assertIn(field.getInstance(), (self.text_field, self.lookupfield, self.inactive_field))

	def test_get_field_list_with_contributor(self):
		user = self._authenticate('diego')
		fields = authorization.featuretypes.get_list_field(user, self.private_project.id, self.active_feature_type.id)
		self.assertEqual(len(fields), 2)

		for field in fields:
			self.assertIn(field.getInstance(), (self.text_field, self.lookupfield))

	def test_get_field_list_with_view_member(self):
		user = self._authenticate('luis')
		fields = authorization.featuretypes.get_list_field(user, self.private_project.id, self.active_feature_type.id)
		self.assertEqual(len(fields), 2)

		for field in fields:
			self.assertIn(field.getInstance(), (self.text_field, self.lookupfield))

	def test_get_field_list_with_non_member(self):
		user = self._authenticate('mehmet')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.get_list_field(user, self.private_project.id, self.active_feature_type.id)

	###########################################################################
	# GET SINGLE FIELDS
	###########################################################################

	def test_get_single_field_with_admin(self):
		user = self._authenticate('eric')
		fields = self.active_feature_type.field_set.all()
		for field in fields:
			self.assertEqual(field.getInstance(), authorization.featuretypes.get_single_field(user, self.private_project.id, self.active_feature_type.id, field.id))

	def test_get_single_field_with_contributor(self):
		user = self._authenticate('diego')
		fields = self.active_feature_type.field_set.all()
		for field in fields:
			if field.id == self.inactive_field.id:
				with self.assertRaises(PermissionDenied):
					self.assertEqual(field.getInstance(), authorization.featuretypes.get_single_field(user, self.private_project.id, self.active_feature_type.id, field.id))
			else:
				self.assertEqual(field.getInstance(), authorization.featuretypes.get_single_field(user, self.private_project.id, self.active_feature_type.id, field.id))

	def test_get_single_field_with_view_member(self):
		user = self._authenticate('luis')
		fields = self.active_feature_type.field_set.all()
		for field in fields:
			if field.id == self.inactive_field.id:
				with self.assertRaises(PermissionDenied):
					self.assertEqual(field.getInstance(), authorization.featuretypes.get_single_field(user, self.private_project.id, self.active_feature_type.id, field.id))
			else:
				self.assertEqual(field.getInstance(), authorization.featuretypes.get_single_field(user, self.private_project.id, self.active_feature_type.id, field.id))

	def test_get_single_field_with_non_member(self):
		user = self._authenticate('mehmet')
		fields = self.active_feature_type.field_set.all()
		for field in fields:
			with self.assertRaises(PermissionDenied):
				self.assertEqual(field.getInstance(), authorization.featuretypes.get_single_field(user, self.private_project.id, self.active_feature_type.id, field.id))

	###########################################################################
	# CREATE FIELD
	###########################################################################

	def test_create_field_with_admin(self):
		user = self._authenticate('eric')
		field = authorization.featuretypes.create_field(user, self.private_project.id, self.active_feature_type.id, {"type": "TEXT", "key": "testkey", "name": "new field", "description": "description"})
		self.assertEqual(field.name, "new field")

	def test_create_field_with_contributor(self):
		user = self._authenticate('diego')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.create_field(user, self.private_project.id, self.active_feature_type.id, {"type": "TEXT", "name": "new field", "key": "testkey", "description": "description"})

	def test_create_field_with_view_member(self):
		user = self._authenticate('luis')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.create_field(user, self.private_project.id, self.active_feature_type.id, {"type": "TEXT", "name": "new field", "key": "testkey", "description": "description"})

	def test_create_field_with_non_member(self):
		user = self._authenticate('mehmet')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.create_field(user, self.private_project.id, self.active_feature_type.id, {"type": "TEXT", "name": "new field", "key": "testkey", "description": "description"})

	###########################################################################
	# UPDATE FIELD
	###########################################################################

	def test_update_field_with_admin(self):
		user = self._authenticate('eric')
		field = authorization.featuretypes.update_field(user, self.private_project.id, self.active_feature_type.id, self.text_field.id, {"description": "updated"})
		self.assertEqual(field.description, "updated")

	def test_update_field_with_contributor(self):
		user = self._authenticate('diego')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.update_field(user, self.private_project.id, self.active_feature_type.id, self.text_field.id, {"description": "updated"})

	def test_update_field_with_view_member(self):
		user = self._authenticate('luis')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.update_field(user, self.private_project.id, self.active_feature_type.id, self.text_field.id, {"description": "updated"})

	def test_update_field_with_non_member(self):
		user = self._authenticate('mehmet')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.update_field(user, self.private_project.id, self.active_feature_type.id, self.text_field.id, {"description": "updated"})

	###########################################################################
	# ADD LOOKUP VALUES
	###########################################################################

	def test_add_lookup_with_admin(self):
		user = self._authenticate('eric')
		field = authorization.featuretypes.add_lookup_value(user, self.private_project.id, self.active_feature_type.id, self.lookupfield.id, {"name": "Kermit"})
		self.assertEqual(len(field.lookupvalue_set.all()), 2)

	def test_update_field_with_contributor(self):
		user = self._authenticate('diego')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.add_lookup_value(user, self.private_project.id, self.active_feature_type.id, self.lookupfield.id, {"name": "Kermit"})

	def test_update_field_with_view_member(self):
		user = self._authenticate('luis')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.add_lookup_value(user, self.private_project.id, self.active_feature_type.id, self.lookupfield.id, {"name": "Kermit"})

	def test_update_field_with_non_member(self):
		user = self._authenticate('mehmet')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.add_lookup_value(user, self.private_project.id, self.active_feature_type.id, self.lookupfield.id, {"name": "Kermit"})

	###########################################################################
	# REMOVE LOOKUP VALUES
	###########################################################################

	def test_add_lookup_with_admin(self):
		user = self._authenticate('eric')
		field = authorization.featuretypes.remove_lookup_value(user, self.private_project.id, self.active_feature_type.id, self.lookupfield.id, self.lookupvalue.id)
		self.assertEqual(len(field.lookupvalue_set.active()), 0)

	def test_update_field_with_contributor(self):
		user = self._authenticate('diego')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.remove_lookup_value(user, self.private_project.id, self.active_feature_type.id, self.lookupfield.id, self.lookupvalue.id)

	def test_update_field_with_view_member(self):
		user = self._authenticate('luis')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.remove_lookup_value(user, self.private_project.id, self.active_feature_type.id, self.lookupfield.id, self.lookupvalue.id)

	def test_update_field_with_non_member(self):
		user = self._authenticate('mehmet')
		with self.assertRaises(PermissionDenied):
			authorization.featuretypes.remove_lookup_value(user, self.private_project.id, self.active_feature_type.id, self.lookupfield.id, self.lookupvalue.id)