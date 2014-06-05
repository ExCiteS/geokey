import json
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from projects.tests.model_factories import UserF, ProjectF
from dataviews.tests.model_factories import ViewFactory

from .model_factories import ObservationFactory, CommentFactory
from ..views import MyObservationComments, MyObservationSingleComment
from ..models import Observation


class GetComments(APITestCase):
    def setUp(self):
        self.creator = UserF.create()
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor, self.creator]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
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
        url = reverse('api:myobservations_comments', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = factory.get(url)
        force_authenticate(request, user=user)
        view = MyObservationComments.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_get_comments_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_with_view_member(self):
        view_member = UserF.create()

        ViewFactory(add_viewers=[view_member], **{
            'project': self.project
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_comments_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_comments_with_creator(self):
        response = self.get_response(self.creator)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AddCommentTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.creator = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor, self.creator]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        url = reverse('api:myobservations_comments', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = factory.post(url, {'text': 'A comment to the observation'})
        force_authenticate(request, user=user)
        view = MyObservationComments.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        ViewFactory(add_viewers=[view_member], **{
            'project': self.project
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_comment_to_observation_with_creator(self):
        response = self.get_response(self.creator)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddCommentToWrongObservation(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        observation = ObservationFactory.create()

        factory = APIRequestFactory()
        url = reverse('api:myobservations_comments', kwargs={
            'project_id': project.id,
            'observation_id': observation.id
        })
        request = factory.post(url, {'text': 'A comment to the observation'})
        force_authenticate(request, user=admin)
        view = MyObservationComments.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id
        ).render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddResponseToCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        observation = ObservationFactory.create(**{
            'project': project,
            'creator': admin
        })
        comment = CommentFactory.create(**{
            'commentto': observation
        })

        factory = APIRequestFactory()
        url = reverse('api:myobservations_comments', kwargs={
            'project_id': project.id,
            'observation_id': observation.id
        })
        request = factory.post(
            url,
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        view = MyObservationComments.as_view()
        response = view(
            request,
            project_id=project.id,
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
        project = ProjectF(add_admins=[admin])
        observation = ObservationFactory.create(**{
            'project': project,
            'creator': admin
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        url = reverse('api:myobservations_comments', kwargs={
            'project_id': project.id,
            'observation_id': observation.id
        })
        request = factory.post(
            url,
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        view = MyObservationComments.as_view()
        response = view(
            request,
            project_id=project.id,
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
        self.creator = UserF.create()
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor, self.creator],
            **{'isprivate': False}
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })
        self.comment = CommentFactory.create(**{
            'commentto': self.observation
        })
        self.comment_to_remove = CommentFactory.create(**{
            'commentto': self.observation,
            'creator': self.creator
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        url = reverse('api:myobservations_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment_to_remove.id
        })
        request = factory.delete(
            url,
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = MyObservationSingleComment.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def test_delete_comment_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_comment_creator(self):
        response = self.get_response(self.creator)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_creator_but_other_comment(self):
        comment = CommentFactory.create(**{
            'commentto': self.observation
        })
        factory = APIRequestFactory()
        url = reverse('api:myobservations_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment_to_remove.id
        })
        request = factory.delete(
            url,
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=self.creator)
        view = MyObservationSingleComment.as_view()
        response = view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id,
            comment_id=comment.id
        ).render()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())


class DeleteWrongComment(APITestCase):
    def test(self):
        creator = UserF.create()
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        observation = ObservationFactory.create(**{
            'project': project,
            'creator': creator
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        url = reverse('api:myobservations_single_comment', kwargs={
            'project_id': project.id,
            'observation_id': observation.id,
            'comment_id': comment.id
        })
        request = factory.delete(url)
        force_authenticate(request, user=admin)
        view = MyObservationSingleComment.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id,
            comment_id=comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
