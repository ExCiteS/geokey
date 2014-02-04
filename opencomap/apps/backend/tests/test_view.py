from base import Test

from django.core.exceptions import PermissionDenied
from opencomap.apps.backend import authorization
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.view import View

class ViewTest(Test):
	def test_access_views_with_non_member(self):
		mehmet = self._authenticate('mehmet')
		views = authorization.views.view_list(mehmet, self.private_project.id)
		self.assertEqual(len(views), 0)

	def test_access_views_with_contributor(self):
		diego = self._authenticate('diego')
		views = authorization.views.view_list(diego, self.private_project.id)
		self.assertEqual(len(views), 0)

	def test_access_views_with_viewgroup_member(self):
		carlos = self._authenticate('carlos')
		views = authorization.views.view_list(carlos, self.private_project.id)
		self.assertEqual(len(views), 1)
		self.assertEqual(views[0], self.active_view)

		zidane = self._authenticate('zidane')
		views = authorization.views.view_list(zidane, self.private_project.id)
		self.assertEqual(len(views), 1)
		self.assertEqual(views[0], self.active_view_2)

	def test_access_views_with_admin(self):
		george = self._authenticate('george')
		views = authorization.views.view_list(george, self.private_project.id)
		self.assertEqual(len(views), 2)
		for view in views:
			self.assertIn(view, (self.active_view, self.active_view_2))

	def test_access_views_with_creator(self):
		eric = self._authenticate('eric')
		views = authorization.views.view_list(eric, self.private_project.id)
		self.assertEqual(len(views), 2)
		for view in views:
			self.assertIn(view, (self.active_view, self.active_view_2))

	def test_access_non_existing_project(self):
		eric = self._authenticate('eric')
		with self.assertRaises(Project.DoesNotExist):
			authorization.views.view(eric, 65564564864, self.active_view.id)

	def test_access_non_existing_view(self):
		eric = self._authenticate('eric')
		with self.assertRaises(View.DoesNotExist):
			authorization.views.view(eric, self.private_project.id, 65564564864)

	def test_access_single_view_with_non_member(self):
		mehmet = self._authenticate('mehmet')
		views = View.objects.all()
		for view in views:
			with self.assertRaises(PermissionDenied):
				authorization.views.view(mehmet, self.private_project.id, view.id)

	def test_access_single_view_with_contributor(self):
		diego = self._authenticate('diego')
		views = View.objects.all()
		for view in views:
			with self.assertRaises(PermissionDenied):
				authorization.views.view(diego, self.private_project.id, view.id)

	def test_access_single_view_with_viewgroup_member(self):
		carlos = self._authenticate('carlos')
		views = View.objects.all()
		for view in views:
			if view.name == 'Active View':
				self.assertEqual(view, authorization.views.view(carlos, self.private_project.id, view.id))
			else:
				with self.assertRaises(PermissionDenied):
					authorization.views.view(carlos, self.private_project.id, view.id)

	def test_access_single_view_with_admins(self):
		eric = self._authenticate('eric')
		views = View.objects.all()
		for view in views:
			self.assertEqual(view, authorization.views.view(eric, self.private_project.id, view.id))

	def test_update_view_with_project_admin(self):
		eric = self._authenticate('eric')
		george = self._authenticate('george')
		for view in self.private_project.view_set.all():
			try:
				authorization.views.update(george, self.private_project.id, view.id, {"description": "new description"})
			except PermissionDenied: 
				self.fail('views.update() raised PermissionDenied unexpectedly')

			try:
				authorization.views.update(eric, self.private_project.id, view.id, {"description": "new description"})
			except PermissionDenied: 
				self.fail('views.update() raised PermissionDenied unexpectedly')

	def test_update_view_with_view_admin(self):
		carlos = self._authenticate('carlos')
		for view in self.private_project.view_set.all():
			if view.name == 'Active View':
				try:
					authorization.views.update(carlos, self.private_project.id, view.id, {"description": "new description"})
				except PermissionDenied: 
					self.fail('views.update() raised PermissionDenied unexpectedly')
			else: 
				with self.assertRaises(PermissionDenied):
					authorization.views.update(carlos, self.private_project.id, view.id, {"description": "new description"})

	def test_update_view_with_non_member(self):
		mehmet = self._authenticate('mehmet')
		for view in self.private_project.view_set.all():
			with self.assertRaises(PermissionDenied):
				authorization.views.update(mehmet, self.private_project.id, view.id, {"description": "new description"})