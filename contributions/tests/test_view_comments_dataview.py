import json

from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from projects.tests.model_factories import UserF, ProjectF
from observationtypes.tests.model_factories import ObservationTypeFactory
from dataviews.tests.model_factories import (
    ViewFactory, RuleFactory
)
from users.tests.model_factories import UserGroupF, ViewUserGroupFactory

from .model_factories import ObservationFactory, CommentFactory
from ..views import ViewComments, ViewSingleComment
from ..models import Observation


class GetCommentsView(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        observation_type = ObservationTypeFactory(**{'project': self.project})
        self.view = ViewFactory(**{'project': self.project})
        RuleFactory(**{'view': self.view, 'observation_type': observation_type})

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'observationtype': observation_type
        })
        comment = CommentFactory.create(**{
            'commentto': self.observation
        })
        response = CommentFactory.create(**{
            'commentto': self.observation,
            'respondsto': comment
        })
        CommentFactory.create(**{
            'commentto': self.observation,
            'respondsto': response
        })
        CommentFactory.create(**{
            'commentto': self.observation,
            'respondsto': comment
        })
        CommentFactory.create(**{
            'commentto': self.observation
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': self.project.id,
                'view_id': self.view.id,
                'observation_id': self.observation.id
            }
        )
        request = factory.get(url)
        force_authenticate(request, user=user)
        view = ViewComments.as_view()
        return view(
            request,
            project_id=self.project.id,
            view_id=self.view.id,
            observation_id=self.observation.id
        ).render()

    def test_get_comments_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_with_view_member(self):
        view_member = UserF.create()
        ViewFactory.create(
            add_viewers=[view_member],
            **{'project': self.project}
        )

        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_comments_with_view_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_comments_with_view_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AddCommentToViewTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        observation_type = ObservationTypeFactory(**{'project': self.project})
        self.view = ViewFactory(**{'project': self.project})
        RuleFactory(**{'view': self.view, 'observation_type': observation_type})

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'observationtype': observation_type
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': self.project.id,
                'view_id': self.view.id,
                'observation_id': self.observation.id
            }
        )
        request = factory.post(url, {'text': 'A comment to the observation'})
        force_authenticate(request, user=user)
        view = ViewComments.as_view()
        return view(
            request,
            project_id=self.project.id,
            view_id=self.view.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are not allowed to access this project.'
        )

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        group = UserGroupF.create(
            add_users=[view_member],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddCommentToWrongObservation(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(
            add_admins=[admin]
        )
        observation = ObservationFactory.create()
        observation_type = ObservationTypeFactory(**{'project': project})
        view = ViewFactory(**{'project': project})
        RuleFactory(**{'view': view, 'observation_type': observation_type})

        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': project.id,
                'view_id': view.id,
                'observation_id': observation.id
            }
        )
        factory = APIRequestFactory()
        request = factory.post(url, {'text': 'A comment to the observation'})
        force_authenticate(request, user=admin)
        dataview = ViewComments.as_view()
        response = dataview(
            request,
            project_id=project.id,
            view_id=view.id,
            observation_id=observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddResponseToCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(
            add_admins=[admin]
        )
        observation_type = ObservationTypeFactory(**{'project': project})
        view = ViewFactory(**{'project': project})
        RuleFactory(**{'view': view, 'observation_type': observation_type})

        observation = ObservationFactory.create(**{
            'project': project,
            'observationtype': observation_type
        })
        comment = CommentFactory.create(**{
            'commentto': observation
        })

        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': project.id,
                'view_id': view.id,
                'observation_id': observation.id
            }
        )
        factory = APIRequestFactory()
        request = factory.post(
            url,
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        dataview = ViewComments.as_view()
        response = dataview(
            request,
            project_id=project.id,
            view_id=view.id,
            observation_id=observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content).get('respondsto'),
            comment.id
        )


class AddResponseToWrongCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(
            add_admins=[admin]
        )
        observation_type = ObservationTypeFactory(**{'project': project})
        view = ViewFactory(**{'project': project})
        RuleFactory(**{'view': view, 'observation_type': observation_type})

        observation = ObservationFactory.create(**{
            'project': project,
            'observationtype': observation_type
        })
        comment = CommentFactory.create()

        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': project.id,
                'view_id': view.id,
                'observation_id': observation.id
            }
        )
        factory = APIRequestFactory()
        request = factory.post(
            url,
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        dataview = ViewComments.as_view()
        response = dataview(
            request,
            project_id=project.id,
            view_id=view.id,
            observation_id=observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'The comment you try to respond to is not a comment to the '
            'observation.'
        )


class DeleteCommentTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.view_member = UserF.create()
        self.commentor = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        observation_type = ObservationTypeFactory(**{'project': self.project})
        self.view = ViewFactory(**{'project': self.project})
        group = UserGroupF.create(
            add_users=[self.view_member, self.commentor],
            **{'project': self.view.project}
        )
        ViewUserGroupFactory.create(
            **{'view': self.view, 'usergroup': group}
        )
        RuleFactory(**{'view': self.view, 'observation_type': observation_type})

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'observationtype': observation_type
        })

        self.comment = CommentFactory.create(**{
            'commentto': self.observation
        })
        self.comment_to_remove = CommentFactory.create(**{
            'commentto': self.observation,
            'creator': self.commentor
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        url = reverse(
            'api:view_single_comment',
            kwargs={
                'project_id': self.project.id,
                'view_id': self.view.id,
                'observation_id': self.observation.id,
                'comment_id': self.comment_to_remove.id
            }
        )
        request = factory.delete(url)
        force_authenticate(request, user=user)
        view = ViewSingleComment.as_view()
        return view(
            request,
            project_id=self.project.id,
            view_id=self.view.id,
            observation_id=self.observation.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def test_delete_comment_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_view_comment_creator(self):
        response = self.get_response(self.commentor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_view_member(self):
        response = self.get_response(self.view_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are neither the author if this comment nor a project '
            'administrator and therefore not eligable to delete this comment.'
        )

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_non_member(self):
        response = self.get_response(self.non_member)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are not allowed to access this project.'
        )

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())


class DeleteWrongComment(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        observation_type = ObservationTypeFactory(**{'project': project})
        view = ViewFactory(**{'project': project})
        RuleFactory(**{'view': view, 'observation_type': observation_type})

        observation = ObservationFactory.create(**{
            'project': project,
            'observationtype': observation_type
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        factory = APIRequestFactory()
        url = reverse(
            'api:view_single_comment',
            kwargs={
                'project_id': project.id,
                'view_id': view.id,
                'observation_id': observation.id,
                'comment_id': comment.id
            }
        )
        request = factory.delete(url)
        force_authenticate(request, user=admin)
        dataview = ViewSingleComment.as_view()
        response = dataview(
            request,
            project_id=project.id,
            view_id=view.id,
            observation_id=observation.id,
            comment_id=comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
