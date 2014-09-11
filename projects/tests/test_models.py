from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from nose.tools import raises

from dataviews.tests.model_factories import ViewFactory
from users.tests.model_factories import UserF, UserGroupF, ViewUserGroupFactory

from .model_factories import ProjectF
from ..models import Project


class CreateProjectTest(TestCase):
    def test_create_project(self):
        creator = UserF.create()

        project = Project.create(
            'Test', 'Test desc', True, True, creator
        )
        self.assertIn(creator, project.admins.all())


class ProjectTest(TestCase):
    @raises(Project.DoesNotExist)
    def test_delete_project(self):
        project = ProjectF.create()
        project.delete()
        Project.objects.get(pk=project.id)

    def test_str(self):
        project = ProjectF.create(**{
            'name': 'Name',
            'status': 'inactive',
            'isprivate': False
        })
        self.assertEqual(
            str(project),
            'Name status: inactive private: False'
        )


class PrivateProjectTest(TestCase):
    def setUp(self):
        self.moderator_all = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_all = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_all = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': True,
            'all_contrib_isprivate': True,
            'everyone_contributes': False
        })
        self.moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.view = ViewFactory(
            **{'project': self.project, 'isprivate': True}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_all))
        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_all))
        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_all))
        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_all))
        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_all))
        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_all))
        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertFalse(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def test_can_access_all(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_all))
        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_all))
        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_all))
        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PrivateProjectTest_PublicView(TestCase):
    def setUp(self):
        self.moderator_all = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_all = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_all = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': True,
            'all_contrib_isprivate': True,
            'everyone_contributes': False
        })
        self.moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.view = ViewFactory(
            **{'project': self.project, 'isprivate': False}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_all))
        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_all))
        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_all))
        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_all))
        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_all))
        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_all))
        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertTrue(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def test_can_access_all(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_all))
        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_all))
        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_all))
        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PrivateProjectTest_PublicAll(TestCase):
    def setUp(self):
        self.moderator_all = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_all = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_all = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': True,
            'all_contrib_isprivate': False,
            'everyone_contributes': False
        })
        self.moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.view = ViewFactory(
            **{'project': self.project, 'isprivate': True}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_all))
        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_all))
        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_all))
        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_all))
        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_all))
        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_all))
        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertTrue(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def test_can_access_all(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer))

    def can_contribute(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_all))
        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_all))
        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_all))
        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PrivateProjectTest_PublicAll_PublicView(TestCase):
    def setUp(self):
        self.moderator_all = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_all = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_all = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': True,
            'all_contrib_isprivate': False,
            'everyone_contributes': False
        })
        self.moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.view = ViewFactory(
            **{'project': self.project, 'isprivate': False}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_all))
        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_all))
        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_all))
        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_all))
        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_all))
        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_all))
        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertTrue(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def test_can_access_all(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer))

    def can_contribute(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_all))
        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_all))
        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_all))
        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PublicProjectTest(TestCase):
    def setUp(self):
        self.moderator_all = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_all = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_all = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': False,
            'all_contrib_isprivate': True,
            'everyone_contributes': False
        })
        self.moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.view = ViewFactory(
            **{'project': self.project, 'isprivate': True}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_all))
        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_all))
        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_all))
        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_all))
        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_all))
        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_all))
        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertFalse(self.project.can_access(self.viewer))

        self.assertFalse(self.project.can_access(self.some_dude))
        self.assertFalse(self.project.can_access(AnonymousUser()))

    def test_can_access_all(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_all))
        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_all))
        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_all))
        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PublicProjectTest_PublicView(TestCase):
    def setUp(self):
        self.moderator_all = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_all = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_all = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': False,
            'all_contrib_isprivate': True,
            'everyone_contributes': False
        })
        self.moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.view = ViewFactory(
            **{'project': self.project, 'isprivate': False}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_all))
        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_all))
        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_all))
        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_all))
        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_all))
        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_all))
        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertTrue(self.project.can_access(self.viewer))

        self.assertTrue(self.project.can_access(self.some_dude))
        self.assertTrue(self.project.can_access(AnonymousUser()))

    def test_can_access_all(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_all))
        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_all))
        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_all))
        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PublicProjectTest_PublicAll(TestCase):
    def setUp(self):
        self.moderator_all = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_all = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_all = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': False,
            'all_contrib_isprivate': False,
            'everyone_contributes': False
        })
        self.moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.view = ViewFactory(
            **{'project': self.project, 'isprivate': True}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_all))
        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_all))
        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_all))
        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_all))
        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_all))
        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_all))
        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertTrue(self.project.can_access(self.viewer))

        self.assertTrue(self.project.can_access(self.some_dude))
        self.assertTrue(self.project.can_access(AnonymousUser()))

    def test_can_access_all(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer))

        self.assertTrue(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertTrue(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_all))
        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_all))
        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_all))
        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))


class PublicProjectTest_PublicAll_PublicView(TestCase):
    def setUp(self):
        self.moderator_all = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_all = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_all = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(**{
            'isprivate': False,
            'all_contrib_isprivate': False,
            'everyone_contributes': False
        })
        self.moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.view = ViewFactory(
            **{'project': self.project, 'isprivate': False}
        )
        self.moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': self.viewers_view})

        self.moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_is_admin(self):
        self.assertTrue(self.project.is_admin(self.project.creator))

        self.assertFalse(self.project.is_admin(self.moderator_all))
        self.assertFalse(self.project.is_admin(self.moderator_view))
        self.assertFalse(self.project.is_admin(self.moderator))

        self.assertFalse(self.project.is_admin(self.contributor_all))
        self.assertFalse(self.project.is_admin(self.contributor_view))
        self.assertFalse(self.project.is_admin(self.contributor))

        self.assertFalse(self.project.is_admin(self.viewer_all))
        self.assertFalse(self.project.is_admin(self.viewer_view))
        self.assertFalse(self.project.is_admin(self.viewer))

        self.assertFalse(self.project.is_admin(self.some_dude))
        self.assertFalse(self.project.is_admin(AnonymousUser()))

    def test_can_access(self):
        self.assertTrue(self.project.can_access(self.project.creator))

        self.assertTrue(self.project.can_access(self.moderator_all))
        self.assertTrue(self.project.can_access(self.moderator_view))
        self.assertTrue(self.project.can_access(self.moderator))

        self.assertTrue(self.project.can_access(self.contributor_all))
        self.assertTrue(self.project.can_access(self.contributor_view))
        self.assertTrue(self.project.can_access(self.contributor))

        self.assertTrue(self.project.can_access(self.viewer_all))
        self.assertTrue(self.project.can_access(self.viewer_view))
        self.assertTrue(self.project.can_access(self.viewer))

        self.assertTrue(self.project.can_access(self.some_dude))
        self.assertTrue(self.project.can_access(AnonymousUser()))

    def test_can_access_all(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.viewer))

        self.assertTrue(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertTrue(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_contribute(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def can_moderate(self):
        self.assertTrue(self.project.can_access_all_contributions(
            self.project.creator))

        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_all))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator_view))
        self.assertTrue(self.project.can_access_all_contributions(
            self.moderator))

        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.contributor))

        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_all))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer_view))
        self.assertFalse(self.project.can_access_all_contributions(
            self.viewer))

        self.assertFalse(self.project.can_access_all_contributions(
            self.some_dude))
        self.assertFalse(self.project.can_access_all_contributions(
            AnonymousUser()))

    def is_involved(self):
        self.assertTrue(self.project.is_involved(self.project.creator))

        self.assertTrue(self.project.is_involved(self.moderator_all))
        self.assertTrue(self.project.is_involved(self.moderator_view))
        self.assertTrue(self.project.is_involved(self.moderator))

        self.assertTrue(self.project.is_involved(self.contributor_all))
        self.assertTrue(self.project.is_involved(self.contributor_view))
        self.assertTrue(self.project.is_involved(self.contributor))

        self.assertTrue(self.project.is_involved(self.viewer_all))
        self.assertTrue(self.project.is_involved(self.viewer_view))
        self.assertTrue(self.project.is_involved(self.viewer))

        self.assertFalse(self.project.is_involved(self.some_dude))
        self.assertFalse(self.project.is_involved(AnonymousUser()))