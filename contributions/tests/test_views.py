from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from observationtypes.tests.model_factories import ObservationTypeFactory
from dataviews.tests.model_factories import (
    ViewFactory, RuleFactory, ViewGroupFactory
)

from .model_factories import ObservationFactory

from ..views import (
    MySingleObservation, SingleProjectObservation, SingleViewObservation,
    ProjectComment, ViewComment
)
from ..models import Observation


class SingleProjectObservationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.creator])
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    @raises(PermissionDenied)
    def test_get_object_with_creator(self):
        view = SingleProjectObservation()
        view.get_object(
            self.creator, self.observation.project.id, self.observation.id)

    def test_get_object_with_admin(self):
        view = SingleProjectObservation()
        observation = view.get_object(
            self.admin, self.observation.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = SingleProjectObservation()
        view.get_object(
            some_dude, self.observation.project.id, self.observation.id)


class SingleViewObservationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.creator])
        })

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

    @raises(PermissionDenied)
    def test_get_object_with_creator_not_viewmember(self):
        view = SingleViewObservation()
        view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )

    def test_get_object_with_creator_is_viewmember(self):
        ViewGroupFactory(add_users=[self.creator], **{
            'view': self.view
        })
        view = SingleViewObservation()
        observation = view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_with_admin(self):
        view = SingleViewObservation()
        observation = view.get_object(
            self.admin, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_with_view_member_not_creator(self):
        view_member = UserF.create()
        ViewGroupFactory(add_users=[view_member], **{
            'view': self.view
        })
        view = SingleViewObservation()
        view.get_object(
            view_member, self.observation.project.id,
            self.view.id, self.observation.id
        )


class MySingleObservationTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.creator])
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def test_get_object_with_creator(self):
        view = MySingleObservation()
        observation = view.get_object(
            self.creator, self.observation.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(Observation.DoesNotExist)
    def test_get_object_with_admin(self):
        view = MySingleObservation()
        view.get_object(
            self.admin, self.observation.project.id, self.observation.id)

    @raises(PermissionDenied)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = MySingleObservation()
        view.get_object(
            some_dude, self.observation.project.id, self.observation.id)


class ProjectCommentTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.creator])
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def test_get_object_with_admin(self):
        view = ProjectComment()
        observation = view.get_object(
            self.admin, self.project.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_with_creator(self):
        view = ProjectComment()
        view.get_object(self.creator, self.project.id, self.observation.id)

    @raises(PermissionDenied)
    def test_get_object_with_some_dude(self):
        some_dude = UserF.create()
        view = ProjectComment()
        view.get_object(some_dude, self.project.id, self.observation.id)


class ViewCommentTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.creator])
        })

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
        view = ViewComment()
        observation = view.get_object(
            self.admin, self.project.id, self.view.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_with_creator_not_viewmember(self):
        view = ViewComment()
        view.get_object(
            self.creator, self.project.id, self.view.id, self.observation.id
        )

    def test_get_object_with_creator_is_viewmember(self):
        ViewGroupFactory(add_users=[self.creator], **{
            'view': self.view
        })
        view = ViewComment()
        observation = view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_with_view_member_not_creator(self):
        view_member = UserF.create()
        ViewGroupFactory(add_users=[view_member], **{
            'view': self.view
        })
        view = ViewComment()
        view.get_object(
            view_member, self.observation.project.id,
            self.view.id, self.observation.id
        )
