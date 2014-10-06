from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser

from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF
from projects.models import Project
from .model_factories import ViewFactory

from ..models import View


class TestPublicViews(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.view1_user = UserF.create()
        self.view2_user = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            **{'isprivate': False}
        )
        self.view1 = ViewFactory(add_viewers=[self.view1_user], **{
            'project': self.project
        })
        self.view2 = ViewFactory(add_viewers=[self.view2_user], **{
            'project': self.project
        })
        self.view1_public = ViewFactory(add_viewers=[self.view1_user], **{
            'project': self.project,
            'isprivate': False
        })
        self.view2_public = ViewFactory(add_viewers=[self.view2_user], **{
            'project': self.project,
            'isprivate': False
        })

    def test_get_list_with_admin(self):
        views = View.objects.get_list(self.admin, self.project.id)
        self.assertEqual(len(views), 4)

    def test_get_list_with_anonymous(self):
        views = View.objects.get_list(AnonymousUser(), self.project.id)
        self.assertEqual(len(views), 2)
        self.assertIn(self.view1_public, views)
        self.assertIn(self.view2_public, views)
        self.assertNotIn(self.view1, views)
        self.assertNotIn(self.view2, views)

    def test_get_list_with_non_member(self):
        non_member = UserF.create()
        views = View.objects.get_list(non_member, self.project.id)
        self.assertEqual(len(views), 2)
        self.assertIn(self.view1_public, views)
        self.assertIn(self.view2_public, views)
        self.assertNotIn(self.view1, views)
        self.assertNotIn(self.view2, views)

    def test_get_list_with_view1_user(self):
        views = View.objects.get_list(self.view1_user, self.project.id)
        self.assertEqual(len(views), 3)
        self.assertIn(self.view1_public, views)
        self.assertIn(self.view2_public, views)
        self.assertIn(self.view1, views)
        self.assertNotIn(self.view2, views)

    def test_get_list_with_view2_user(self):
        views = View.objects.get_list(self.view2_user, self.project.id)
        self.assertEqual(len(views), 3)
        self.assertIn(self.view1_public, views)
        self.assertIn(self.view2_public, views)
        self.assertNotIn(self.view1, views)
        self.assertIn(self.view2, views)


class TestSinglePublicView(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.view_user = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            **{'isprivate': False}
        )
        self.private_view = ViewFactory(add_viewers=[self.view_user], **{
            'project': self.project
        })
        self.public_view = ViewFactory(add_viewers=[self.view_user], **{
            'project': self.project,
            'isprivate': False
        })

    def test_get_public_view_with_admin(self):
        view = View.objects.get_single(
            self.admin, self.project.id, self.public_view.id)
        self.assertEqual(view, self.public_view)

    def test_get_private_view_with_admin(self):
        view = View.objects.get_single(
            self.admin, self.project.id, self.private_view.id)
        self.assertEqual(view, self.private_view)

    def test_get_public_view_with_view_user(self):
        view = View.objects.get_single(
            self.view_user, self.project.id, self.public_view.id)
        self.assertEqual(view, self.public_view)

    def test_get_private_view_with_view_user(self):
        view = View.objects.get_single(
            self.view_user, self.project.id, self.private_view.id)
        self.assertEqual(view, self.private_view)

    def test_get_public_view_with_anonymous(self):
        view = View.objects.get_single(
            AnonymousUser(), self.project.id, self.public_view.id)
        self.assertEqual(view, self.public_view)

    @raises(View.DoesNotExist)
    def test_get_private_view_with_anonymous(self):
        View.objects.get_single(
            AnonymousUser(), self.project.id, self.private_view.id)

    def test_get_public_view_with_some_dude(self):
        view = View.objects.get_single(
            UserF.create(), self.project.id, self.public_view.id)
        self.assertEqual(view, self.public_view)

    @raises(View.DoesNotExist)
    def test_get_private_view_with_some_dude(self):
        View.objects.get_single(
            UserF.create(), self.project.id, self.private_view.id)


class TestManager(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view1_user = UserF.create()
        self.view2_user = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.view1 = ViewFactory(add_viewers=[self.view1_user], **{
            'project': self.project
        })
        self.view2 = ViewFactory(add_viewers=[self.view2_user], **{
            'project': self.project
        })

    def test_get_views_with_admin(self):
        views = View.objects.get_list(self.admin, self.project.id)
        self.assertEqual(len(views), 2)

    def test_get_views_with_view1_user(self):
        views = View.objects.get_list(self.view1_user, self.project.id)
        self.assertEqual(len(views), 1)
        self.assertIn(self.view1, views)
        self.assertNotIn(self.view2, views)

    def test_get_views_with_view2_user(self):
        views = View.objects.get_list(self.view2_user, self.project.id)
        self.assertEqual(len(views), 1)
        self.assertIn(self.view2, views)
        self.assertNotIn(self.view1, views)

    def test_get_views_with_contributor(self):
        views = View.objects.get_list(self.contributor, self.project.id)
        self.assertEqual(len(views), 0)

    @raises(Project.DoesNotExist)
    def test_get_views_with_non_member(self):
        View.objects.get_list(self.non_member, self.project.id)

    def test_get_single_view_with_admin(self):
        view = View.objects.get_single(
            self.admin, self.project.id, self.view1.id)
        self.assertEqual(view, self.view1)

    @raises(View.DoesNotExist)
    def test_get_single_view_with_contributor(self):
        View.objects.get_single(
            self.contributor, self.project.id, self.view1.id)

    def test_get_single_view_with_view_user(self):
        view = View.objects.get_single(
            self.view1_user, self.project.id, self.view1.id)
        self.assertEqual(view, self.view1)

    @raises(View.DoesNotExist)
    def test_get_single_view_with_wrong_view_user(self):
        View.objects.get_single(
            self.view2_user, self.project.id, self.view1.id)

    @raises(Project.DoesNotExist)
    def test_get_single_view_with_non_member(self):
        View.objects.get_single(
            self.non_member, self.project.id, self.view1.id)

    def test_get_single_view_as_admin_with_admin(self):
        view = View.objects.as_admin(
            self.admin, self.project.id, self.view1.id)
        self.assertEqual(view, self.view1)

    @raises(PermissionDenied)
    def test_get_single_view_as_admin_with_contributor(self):
        View.objects.as_admin(
            self.contributor, self.project.id, self.view1.id)

    @raises(PermissionDenied)
    def test_get_single_view_as_admin_with_view_member(self):
        View.objects.as_admin(
            self.view1_user, self.project.id, self.view1.id)

    @raises(Project.DoesNotExist)
    def test_get_single_view_as_admin_with_non_member(self):
        View.objects.as_admin(
            self.non_member, self.project.id, self.view1.id)
