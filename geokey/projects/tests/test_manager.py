from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from geokey.datagroupings.tests.model_factories import GroupingFactory
from geokey.users.tests.model_factories import (
    UserF, UserGroupF, GroupingUserGroupFactory
)

from .model_factories import ProjectF
from ..models import Project


class ProjectListTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.moderator_view = UserF.create()
        self.moderator = UserF.create()
        self.contributor_view = UserF.create()
        self.contributor = UserF.create()
        self.viewer_view = UserF.create()
        self.viewer = UserF.create()
        self.some_dude = UserF.create()

        self.private_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Private',
                'isprivate': True,
                'everyone_contributes': 'false'
            })

        self.private_view = GroupingFactory(
            **{'project': self.private_project, 'isprivate': True}
        )
        self.private_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.private_project,
                'can_moderate': True
            })
        self.private_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.private_project,
                'can_contribute': True
            })
        self.private_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.private_project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(**{
            'grouping': self.private_view,
            'usergroup': self.private_moderators_view}
        )
        GroupingUserGroupFactory.create(**{
            'grouping': self.private_view,
            'usergroup': self.private_contributors_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.private_view,
            'usergroup': self.private_viewers_view
        })

        self.private_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.private_project,
                'can_moderate': True
            })
        self.private_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.private_project,
                'can_contribute': True
            })
        self.private_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.private_project,
                'can_contribute': False,
                'can_moderate': False
            })

        self.private_publicview_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Private with public view',
                'isprivate': True,
                'everyone_contributes': 'false'
            })

        self.private_publicview_view = GroupingFactory(
            **{'project': self.private_publicview_project, 'isprivate': False}
        )
        self.private_publicview_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.private_publicview_project,
                'can_moderate': True
            })
        self.private_publicview_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.private_publicview_project,
                'can_contribute': True
            })
        self.private_publicview_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.private_publicview_project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(**{
            'grouping': self.private_publicview_view,
            'usergroup': self.private_publicview_moderators_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.private_publicview_view,
            'usergroup': self.private_publicview_contributors_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.private_publicview_view,
            'usergroup': self.private_publicview_viewers_view
        })

        self.private_publicview_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.private_publicview_project,
                'can_moderate': True
            })
        self.private_publicview_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.private_publicview_project,
                'can_contribute': True
            })
        self.private_publicview_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.private_publicview_project,
                'can_contribute': False,
                'can_moderate': False
            })

        self.private_publicviews_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Private with public views',
                'isprivate': True,
                'everyone_contributes': 'false'
            })

        self.private_publicviews_view = GroupingFactory(
            **{'project': self.private_publicviews_project, 'isprivate': False}
        )
        self.private_publicviews_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.private_publicviews_project,
                'can_moderate': True
            })
        self.private_publicviews_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': True
            })
        self.private_publicviews_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(**{
            'grouping': self.private_publicviews_view,
            'usergroup': self.private_publicviews_moderators_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.private_publicviews_view,
            'usergroup': self.private_publicviews_contributors_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.private_publicviews_view,
            'usergroup': self.private_publicviews_viewers_view
        })

        self.private_publicviews_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.private_publicviews_project,
                'can_moderate': True
            })
        self.private_publicviews_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': True
            })
        self.private_publicviews_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': False,
                'can_moderate': False
            })

        self.public_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Public',
                'isprivate': False,
                'everyone_contributes': 'false'
            })

        self.public_view = GroupingFactory(
            **{'project': self.public_project, 'isprivate': True}
        )
        self.public_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.public_project,
                'can_moderate': True
            })
        self.public_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.public_project,
                'can_contribute': True
            })
        self.public_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.public_project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(**{
            'grouping': self.public_view,
            'usergroup': self.public_moderators_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.public_view,
            'usergroup': self.public_contributors_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.public_view,
            'usergroup': self.public_viewers_view
        })

        self.public_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.public_project,
                'can_moderate': True
            })
        self.public_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.public_project,
                'can_contribute': True
            })
        self.public_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.public_project,
                'can_contribute': False,
                'can_moderate': False
            })

        self.public_publicview_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Public with public view',
                'isprivate': False,
                'everyone_contributes': 'false'
            })

        self.public_publicview_view = GroupingFactory(
            **{'project': self.public_publicview_project, 'isprivate': False}
        )
        self.public_publicview_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.public_publicview_project,
                'can_moderate': True
            })
        self.public_publicview_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.public_publicview_project,
                'can_contribute': True
            })
        self.public_publicview_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.public_publicview_project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(**{
            'grouping': self.public_publicview_view,
            'usergroup': self.public_publicview_moderators_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.public_publicview_view,
            'usergroup': self.public_publicview_contributors_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.public_publicview_view,
            'usergroup': self.public_publicview_viewers_view
        })

        self.public_publicview_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.public_publicview_project,
                'can_moderate': True
            })
        self.public_publicview_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.public_publicview_project,
                'can_contribute': True
            })
        self.public_publicview_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.public_publicview_project,
                'can_contribute': False,
                'can_moderate': False
            })

        self.public_publicviews_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'public with all public views',
                'isprivate': False,
                'everyone_contributes': 'false'
            })

        self.public_publicviews_view = GroupingFactory(
            **{'project': self.public_publicviews_project, 'isprivate': False}
        )
        self.public_publicviews_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.public_publicviews_project,
                'can_moderate': True
            })
        self.public_publicviews_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': True
            })
        self.public_publicviews_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': False,
                'can_moderate': False
            })

        GroupingUserGroupFactory.create(**{
            'grouping': self.public_publicviews_view,
            'usergroup': self.public_publicviews_moderators_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.public_publicviews_view,
            'usergroup': self.public_publicviews_contributors_view
        })
        GroupingUserGroupFactory.create(**{
            'grouping': self.public_publicviews_view,
            'usergroup': self.public_publicviews_viewers_view
        })

        self.public_publicviews_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.public_publicviews_project,
                'can_moderate': True
            })
        self.public_publicviews_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': True
            })
        self.public_publicviews_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': False,
                'can_moderate': False
            })

    def test_get_list_with_admin(self):
        projects = Project.objects.get_list(self.admin)
        self.assertEquals(len(projects), 6)

    def test_get_list_with_moderator_view(self):
        projects = Project.objects.get_list(self.moderator_view)
        self.assertEquals(len(projects), 6)

    def test_get_list_with_moderator(self):
        projects = Project.objects.get_list(self.moderator)
        self.assertEquals(len(projects), 6)

    def test_get_list_with_contributor_view(self):
        projects = Project.objects.get_list(self.contributor_view)
        self.assertEquals(len(projects), 6)

    def test_get_list_with_contributor(self):
        projects = Project.objects.get_list(self.contributor)
        self.assertEquals(len(projects), 6)

    def test_get_list_with_viewer_view(self):
        projects = Project.objects.get_list(self.viewer_view)
        self.assertEquals(len(projects), 6)

    def test_get_list_with_viewer(self):
        projects = Project.objects.get_list(self.viewer)
        self.assertEquals(len(projects), 2)

    def test_get_list_with_some_dude(self):
        projects = Project.objects.get_list(self.some_dude)
        self.assertEquals(len(projects), 2)

    def test_get_list_with_anonymous(self):
        projects = Project.objects.get_list(AnonymousUser())
        self.assertEquals(len(projects), 2)


class ProjectAccessTest(TestCase):
    def test_as_admin(self):
        project = ProjectF.create()
        user = UserF.create(**{'is_superuser': True})
        ref = Project.objects.as_admin(user, project.id)
        self.assertEqual(project, ref)

    def test_as_contributor(self):
        admin = UserF.create()
        contributor = UserF.create()
        other = UserF.create()

        project = ProjectF.create(
            add_admins=[admin],
            add_contributors=[contributor],
            add_viewers=[other]
        )

        ref = Project.objects.as_contributor(admin, project.id)
        self.assertEqual(project, ref)

        ref = Project.objects.as_contributor(contributor, project.id)
        self.assertEqual(project, ref)

        try:
            Project.objects.as_contributor(other, project.id)
        except PermissionDenied:
            pass
        else:
            self.fail('PermissionDenied not raise for non contributor')
