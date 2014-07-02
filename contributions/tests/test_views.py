from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from nose.tools import raises
from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF
from observationtypes.tests.model_factories import ObservationTypeFactory
from dataviews.tests.model_factories import (
    ViewFactory, RuleFactory
)
from users.tests.model_factories import UserGroupF, ViewUserGroupFactory

from .model_factories import ObservationFactory, CommentFactory

from ..views import (
    MySingleObservation, SingleProjectObservation, SingleViewObservation,
    ProjectComment, ViewComment
)
from ..models import Observation


class SingleProjectObservationTest(TestCase):
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

    def test_api_with_admin(self):
        CommentFactory.create_batch(5, **{'commentto': self.observation})
        factory = APIRequestFactory()
        url = reverse('api:project_single_observation', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = factory.get(url)
        force_authenticate(request, user=self.admin)
        theview = SingleProjectObservation.as_view()
        response = theview(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id).render()
        self.assertEqual(response.status_code, 200)


class SingleViewObservationTest(TestCase):
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

    @raises(PermissionDenied)
    def test_get_object_with_creator_not_viewmember(self):
        view = SingleViewObservation()
        view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )

    def test_get_object_with_reader(self):
        group = UserGroupF.create(
            add_users=[self.creator],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group, 'can_read': True}
        )

        view = SingleViewObservation()
        observation = view.get_object(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    # @raises(PermissionDenied)
    # def test_get_object_with_not_reader(self):
    #     view_member = UserF.create()
    #     group = UserGroupF.create(
    #         add_users=[view_member],
    #         **{'project': self.view.project}
    #     )
    #     ViewUserGroupFactory.create(
    #         **{'view': self.view, 'usergroup': group, 'can_read': False}
    #     )
    #     view = SingleViewObservation()
    #     view.get_object(
    #         view_member, self.observation.project.id,
    #         self.view.id, self.observation.id
    #     )

    def test_get_object_with_admin(self):
        view = SingleViewObservation()
        observation = view.get_object(
            self.admin, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_for_update_with_creator_not_viewmember(self):
        view = SingleViewObservation()
        view.get_object_for_update(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )

    def test_get_object_with_moderator(self):
        moderator = UserF.create()
        group = UserGroupF.create(
            add_users=[moderator],
            **{'project': self.view.project, 'can_moderate': True}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )

        view = SingleViewObservation()
        observation = view.get_object_for_update(
            moderator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_with_creator_moderator(self):
        group = UserGroupF.create(
            add_users=[self.creator],
            **{'project': self.view.project, 'can_moderate': True}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )

        view = SingleViewObservation()
        observation = view.get_object_for_update(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    @raises(PermissionDenied)
    def test_get_object_with_non_moderator(self):
        non_moderator = UserF.create()
        group = UserGroupF.create(
            add_users=[non_moderator],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group, 'can_read': True}
        )

        view = SingleViewObservation()
        observation = view.get_object_for_update(
            non_moderator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_with_creator_non_moderator(self):
        group = UserGroupF.create(
            add_users=[self.creator],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group, 'can_read': True}
        )

        view = SingleViewObservation()
        observation = view.get_object_for_update(
            self.creator, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)

    def test_get_object_for_update_with_admin(self):
        view = SingleViewObservation()
        observation = view.get_object_for_update(
            self.admin, self.observation.project.id,
            self.view.id, self.observation.id
        )
        self.assertEqual(observation, self.observation)


class MySingleObservationTest(TestCase):
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
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
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
        group = UserGroupF.create(
            add_users=[self.creator],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )
        view = ViewComment()
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
        view = ViewComment()
        view.get_object(
            view_member, self.observation.project.id,
            self.view.id, self.observation.id
        )
