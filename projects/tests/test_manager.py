from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from nose.tools import raises

from dataviews.tests.model_factories import ViewFactory
from users.tests.model_factories import UserF, UserGroupF, ViewUserGroupFactory

from .model_factories import ProjectF
from ..models import Project


class ProjectListTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
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

        self.private_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Private',
                'isprivate': True,
                'all_contrib_isprivate': True,
                'everyone_contributes': False
            })
        self.private_moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.private_project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.private_contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.private_project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.private_viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.private_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.private_view = ViewFactory(
            **{'project': self.private_project, 'isprivate': True}
        )
        self.private_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.private_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.private_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.private_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.private_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.private_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.private_view, 'usergroup': self.private_moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.private_view, 'usergroup': self.private_contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.private_view, 'usergroup': self.private_viewers_view})

        self.private_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.private_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.private_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.private_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.private_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.private_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        self.private_publicview_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Private with public view',
                'isprivate': True,
                'all_contrib_isprivate': True,
                'everyone_contributes': False
            })
        self.private_publicview_moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.private_publicview_project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.private_publicview_contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.private_publicview_project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.private_publicview_viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.private_publicview_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.private_publicview_view = ViewFactory(
            **{'project': self.private_publicview_project, 'isprivate': False}
        )
        self.private_publicview_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.private_publicview_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.private_publicview_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.private_publicview_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.private_publicview_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.private_publicview_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.private_publicview_view, 'usergroup': self.private_publicview_moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.private_publicview_view, 'usergroup': self.private_publicview_contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.private_publicview_view, 'usergroup': self.private_publicview_viewers_view})

        self.private_publicview_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.private_publicview_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.private_publicview_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.private_publicview_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.private_publicview_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.private_publicview_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        self.private_publicall_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Private with public all contributions',
                'isprivate': True,
                'all_contrib_isprivate': False,
                'everyone_contributes': False
            })
        self.private_publicall_moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.private_publicall_project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.private_publicall_contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.private_publicall_project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.private_publicall_viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.private_publicall_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.private_publicall_view = ViewFactory(
            **{'project': self.private_publicall_project, 'isprivate': True}
        )
        self.private_publicall_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.private_publicall_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.private_publicall_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.private_publicall_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.private_publicall_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.private_publicall_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.private_publicall_view, 'usergroup': self.private_publicall_moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.private_publicall_view, 'usergroup': self.private_publicall_contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.private_publicall_view, 'usergroup': self.private_publicall_viewers_view})

        self.private_publicall_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.private_publicall_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.private_publicall_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.private_publicall_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.private_publicall_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.private_publicall_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        self.private_publicviews_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Private with public views',
                'isprivate': True,
                'all_contrib_isprivate': False,
                'everyone_contributes': False
            })
        self.private_publicviews_moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.private_publicviews_project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.private_publicviews_contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.private_publicviews_viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.private_publicviews_view = ViewFactory(
            **{'project': self.private_publicviews_project, 'isprivate': False}
        )
        self.private_publicviews_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.private_publicviews_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.private_publicviews_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.private_publicviews_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.private_publicviews_view, 'usergroup': self.private_publicviews_moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.private_publicviews_view, 'usergroup': self.private_publicviews_contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.private_publicviews_view, 'usergroup': self.private_publicviews_viewers_view})

        self.private_publicviews_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.private_publicviews_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.private_publicviews_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.private_publicviews_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.private_publicviews_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        self.public_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Public',
                'isprivate': False,
                'all_contrib_isprivate': True,
                'everyone_contributes': False
            })
        self.public_moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.public_project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.public_contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.public_project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.public_viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.public_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.public_view = ViewFactory(
            **{'project': self.public_project, 'isprivate': True}
        )
        self.public_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.public_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.public_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.public_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.public_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.public_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.public_view, 'usergroup': self.public_moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.public_view, 'usergroup': self.public_contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.public_view, 'usergroup': self.public_viewers_view})

        self.public_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.public_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.public_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.public_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.public_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.public_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        self.public_publicview_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Public with public view',
                'isprivate': False,
                'all_contrib_isprivate': True,
                'everyone_contributes': False
            })
        self.public_publicview_moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.public_publicview_project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.public_publicview_contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.public_publicview_project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.public_publicview_viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.public_publicview_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.public_publicview_view = ViewFactory(
            **{'project': self.public_publicview_project, 'isprivate': False}
        )
        self.public_publicview_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.public_publicview_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.public_publicview_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.public_publicview_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.public_publicview_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.public_publicview_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.public_publicview_view, 'usergroup': self.public_publicview_moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.public_publicview_view, 'usergroup': self.public_publicview_contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.public_publicview_view, 'usergroup': self.public_publicview_viewers_view})

        self.public_publicview_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.public_publicview_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.public_publicview_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.public_publicview_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.public_publicview_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.public_publicview_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        self.public_publicall_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'Public with public all contributions',
                'isprivate': False,
                'all_contrib_isprivate': False,
                'everyone_contributes': False
            })
        self.public_publicall_moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.public_publicall_project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.public_publicall_contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.public_publicall_project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.public_publicall_viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.public_publicall_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.public_publicall_view = ViewFactory(
            **{'project': self.public_publicall_project, 'isprivate': True}
        )
        self.public_publicall_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.public_publicall_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.public_publicall_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.public_publicall_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.public_publicall_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.public_publicall_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.public_publicall_view, 'usergroup': self.public_publicall_moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.public_publicall_view, 'usergroup': self.public_publicall_contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.public_publicall_view, 'usergroup': self.public_publicall_viewers_view})

        self.public_publicall_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.public_publicall_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.public_publicall_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.public_publicall_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.public_publicall_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.public_publicall_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        self.public_publicviews_project = ProjectF.create(
            add_admins=[self.admin],
            **{
                'name': 'public with all public views',
                'isprivate': False,
                'all_contrib_isprivate': False,
                'everyone_contributes': False
            })
        self.public_publicviews_moderators_all = UserGroupF(
            add_users=[self.moderator_all],
            **{
                'project': self.public_publicviews_project,
                'can_moderate': True,
                'read_all_contrib': True
            })
        self.public_publicviews_contributors_all = UserGroupF(
            add_users=[self.contributor_all],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': True,
                'read_all_contrib': True
            })
        self.public_publicviews_viewers_all = UserGroupF(
            add_users=[self.viewer_all],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': True
            })

        self.public_publicviews_view = ViewFactory(
            **{'project': self.public_publicviews_project, 'isprivate': False}
        )
        self.public_publicviews_moderators_view = UserGroupF(
            add_users=[self.moderator_view],
            **{
                'project': self.public_publicviews_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.public_publicviews_contributors_view = UserGroupF(
            add_users=[self.contributor_view],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.public_publicviews_viewers_view = UserGroupF(
            add_users=[self.viewer_view],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

        ViewUserGroupFactory.create(
            **{'view': self.public_publicviews_view, 'usergroup': self.public_publicviews_moderators_view})
        ViewUserGroupFactory.create(
            **{'view': self.public_publicviews_view, 'usergroup': self.public_publicviews_contributors_view})
        ViewUserGroupFactory.create(
            **{'view': self.public_publicviews_view, 'usergroup': self.public_publicviews_viewers_view})

        self.public_publicviews_moderators = UserGroupF(
            add_users=[self.moderator],
            **{
                'project': self.public_publicviews_project,
                'can_moderate': True,
                'read_all_contrib': False
            })
        self.public_publicviews_contributors = UserGroupF(
            add_users=[self.contributor],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': True,
                'read_all_contrib': False
            })
        self.public_publicviews_viewers = UserGroupF(
            add_users=[self.viewer],
            **{
                'project': self.public_publicviews_project,
                'can_contribute': False,
                'can_moderate': False,
                'read_all_contrib': False
            })

    def test_get_list_with_admin(self):
        projects = Project.objects.get_list(self.admin)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_moderator_all(self):
        projects = Project.objects.get_list(self.moderator_all)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_moderator_view(self):
        projects = Project.objects.get_list(self.moderator_view)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_moderator(self):
        projects = Project.objects.get_list(self.moderator)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_contributor_all(self):
        projects = Project.objects.get_list(self.contributor_all)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_contributor_view(self):
        projects = Project.objects.get_list(self.contributor_view)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_contributor(self):
        projects = Project.objects.get_list(self.contributor)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_viewer_all(self):
        projects = Project.objects.get_list(self.viewer_all)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_viewer_view(self):
        projects = Project.objects.get_list(self.viewer_view)
        self.assertEquals(len(projects), 8)

    def test_get_list_with_viewer(self):
        projects = Project.objects.get_list(self.viewer)
        self.assertEquals(len(projects), 6)

    def test_get_list_with_some_dude(self):
        projects = Project.objects.get_list(self.some_dude)
        self.assertEquals(len(projects), 3)

    def test_get_list_with_anonymous(self):
        projects = Project.objects.get_list(AnonymousUser())
        self.assertEquals(len(projects), 3)
