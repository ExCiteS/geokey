from django.test import TestCase

from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF
from projects.models import Project
from observationtypes.tests.model_factories import ObservationTypeFactory
from dataviews.tests.model_factories import (
    ViewFactory, RuleFactory
)
from dataviews.models import View
from users.tests.model_factories import UserGroupF, ViewUserGroupFactory

from ..model_factories import ObservationFactory

from contributions.views.comments import (
    AllContributionsSingleCommentAPIView,
    GroupingContributionsSingleCommentAPIView
)


class AllContributionsSingleCommentAPIViewTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def test_get_object_with_admin(self):
        view = AllContributionsSingleCommentAPIView()
        observation = view.get_object(
            self.admin, self.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    def test_get_object_with_creator(self):
        view = AllContributionsSingleCommentAPIView()
        view.get_object(self.creator, self.project.id, self.observation.id)

    @raises(Project.DoesNotExist)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = AllContributionsSingleCommentAPIView()
        view.get_object(some_dude, self.project.id, self.observation.id)


class GroupingContributionsSingleCommentAPIViewTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )

        observation_type = ObservationTypeFactory(**{'project': self.project})

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'observationtype': observation_type
        })

        self.view = ViewFactory(**{'project': self.project})
        RuleFactory(**{
            'view': self.view,
            'observation_type': observation_type}
        )

    def test_get_object_with_admin(self):
        view = GroupingContributionsSingleCommentAPIView()
        observation = view.get_object(
            self.admin, self.project.id, self.view.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(View.DoesNotExist)
    def test_get_object_with_creator_not_viewmember(self):
        view = GroupingContributionsSingleCommentAPIView()
        view.get_object(
            self.creator, self.project.id, self.view.id, self.observation.id
        )

    def test_get_object_with_creator_is_viewmember(self):
        group = UserGroupF.create(
            add_users=[self.creator],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )
        view = GroupingContributionsSingleCommentAPIView()
        observation = view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_with_view_member_not_creator(self):
        view_member = UserF.create()
        group = UserGroupF.create(
            add_users=[view_member],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )
        view = GroupingContributionsSingleCommentAPIView()
        view.get_object(
            view_member, self.observation.project.id,
            self.view.id, self.observation.id
        )
