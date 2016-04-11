"""Tests for views of contributions (comments)."""

import json

from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from geokey.projects.tests.model_factories import UserFactory, ProjectFactory
from geokey.projects.models import Project
from geokey.contributions.models import Comment, Observation
from geokey.users.models import User

from geokey.users.tests.model_factories import UserGroupFactory
from ..model_factories import ObservationFactory, CommentFactory

from geokey.contributions.views.comments import (
    CommentsAPIView,
    SingleCommentAPIView,
    CommentAbstractAPIView
)


class CommentAbstractAPIViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.creator = UserFactory.create()
        self.moderator = UserFactory.create()
        self.commenter = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.creator, self.commenter]
        )
        self.moderators = UserGroupFactory(add_users=[self.moderator], **{
            'project': self.project,
            'can_moderate': True
        })
        self.contribution = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'status': 'active'
        })
        self.comment = CommentFactory.create(**{
            'commentto': self.contribution,
            'creator': self.commenter
        })

    def render(self, response):
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {'blah': 'blubb'}
        return response.render()

    def test_create_comment_with_admin(self):
        url = reverse('api:project_comments', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id
        })
        request = self.factory.post(url, {'text': 'Comment'})
        request.user = self.admin
        request.data = {'text': 'Comment'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.create_and_respond(request, self.contribution)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Comment')

    def test_create_reviewcomment_with_admin(self):
        url = reverse('api:project_comments', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id
        })
        request = self.factory.post(
            url, {'text': 'Comment', 'review_status': 'open'}
        )
        request.user = self.admin
        request.data = {'text': 'Comment', 'review_status': 'open'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.create_and_respond(request, self.contribution)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Comment')
        ref = Observation.objects.get(pk=self.contribution.id)
        self.assertEqual(ref.status, 'review')

    def test_create_reviewcomment_to_empty_obs_with_admin(self):
        self.contribution.properties = None
        self.contribution.save()

        url = reverse('api:project_comments', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id
        })
        request = self.factory.post(
            url, {'text': 'Comment', 'review_status': 'open'}
        )
        request.user = self.admin
        request.data = {'text': 'Comment', 'review_status': 'open'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.create_and_respond(request, self.contribution)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Comment')
        ref = Observation.objects.get(pk=self.contribution.id)
        self.assertEqual(ref.status, 'review')

    def test_update_comment_with_admin(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.admin
        request.data = {'text': 'Updated'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.contribution, self.comment)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Updated')
        self.assertEqual(
            Comment.objects.get(pk=self.comment.id).text,
            'Updated'
        )

    def test_update_comment_with_commenter(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.commenter
        request.data = {'text': 'Updated'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.contribution, self.comment)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Updated')
        self.assertEqual(
            Comment.objects.get(pk=self.comment.id).text,
            'Updated'
        )

    def test_update_comment_with_moderator(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.moderator
        request.data = {'text': 'Updated'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.contribution, self.comment)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Updated')
        self.assertEqual(
            Comment.objects.get(pk=self.comment.id).text,
            'Updated'
        )

    @raises(PermissionDenied)
    def test_update_comment_with_creator(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.creator
        request.data = {'text': 'Updated'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.contribution, self.comment)
        )
        self.assertEqual(
            json.loads(response.content).get('text'),
            self.comment.text
        )
        self.assertEqual(
            Comment.objects.get(pk=self.comment.id).text,
            self.comment.text
        )

    def test_update_invalid_comment(self):
        self.project.isprivate = False
        self.project.save()

        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(
            url, {'text': 'Updated', 'review_status': 'blah'}
        )
        force_authenticate(request, user=self.commenter)

        view = SingleCommentAPIView.as_view()
        response = view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id,
            comment_id=self.comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentAbstractAPIViewResolveTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserFactory.create()
        self.creator = UserFactory.create()
        self.moderator = UserFactory.create()
        self.commenter = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.creator, self.commenter]
        )
        self.moderators = UserGroupFactory(add_users=[self.moderator], **{
            'project': self.project,
            'can_moderate': True
        })
        self.contribution = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'status': 'review'
        })
        self.comment = CommentFactory.create(**{
            'commentto': self.contribution,
            'creator': self.commenter,
            'review_status': 'open'
        })

    def render(self, response):
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {'blah': 'blubb'}
        return response.render()

    def test_resolve_comment_with_admin(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.admin
        request.data = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.contribution, self.comment)
        )
        self.assertEqual(
            json.loads(response.content).get('review_status'),
            'resolved'
        )

        reference = Observation.objects.get(pk=self.contribution.id)
        self.assertEqual(reference.status, 'active')
        self.assertIsNotNone(reference.properties)

    def test_resolve_comment_with_invalid_review_status(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.admin
        request.data = {'review_status': 'closed'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.contribution, self.comment)
        )

        ref = Comment.objects.get(pk=self.comment.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ref.review_status, 'open')

    def test_resolve_one_of_two_comment_with_admin(self):
        CommentFactory.create(**{
            'commentto': self.contribution,
            'creator': self.creator,
            'review_status': 'open'
        })

        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.admin
        request.data = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.contribution, self.comment)
        )
        self.assertEqual(
            json.loads(response.content).get('review_status'),
            'resolved'
        )
        self.assertEqual(
            Observation.objects.get(pk=self.contribution.id).status,
            'review'
        )

    def test_resolve_comment_with_moderator(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.moderator
        request.data = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.contribution, self.comment)
        )
        self.assertEqual(
            json.loads(response.content).get('review_status'),
            'resolved'
        )
        self.assertEqual(
            Observation.objects.get(pk=self.contribution.id).status,
            'active'
        )

    @raises(PermissionDenied)
    def test_resolve_comment_with_creator(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.creator
        request.data = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        view.update_and_respond(request, self.contribution, self.comment)

    @raises(PermissionDenied)
    def test_resolve_comment_with_commenter(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.commenter
        request.data = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        view.update_and_respond(request, self.contribution, self.comment)

    @raises(PermissionDenied)
    def test_resolve_comment_with_anonymous(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'contribution_id': self.contribution.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = AnonymousUser()
        request.data = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        view.update_and_respond(request, self.contribution, self.comment)


class SingleCommentAPIViewTest(TestCase):
    def setUp(self):
        self.admin = UserFactory.create()
        self.creator = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.creator]
        )
        self.contribution = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator
        })

    def test_get_contribution_with_admin(self):
        view = SingleCommentAPIView()
        contribution = view.get_contribution(
            self.admin, self.project.id, self.contribution.id)
        self.assertEqual(contribution, self.contribution)

    def test_get_contribution_with_creator(self):
        view = SingleCommentAPIView()
        view.get_contribution(
            self.creator,
            self.project.id,
            self.contribution.id
        )

    @raises(Project.DoesNotExist)
    def test_get_contribution_with_some_dude(self):
        some_dude = UserFactory.create()
        view = SingleCommentAPIView()
        view.get_contribution(
            some_dude,
            self.project.id,
            self.contribution.id
        )


class GetProjectComments(APITestCase):
    def setUp(self):
        self.contributor = UserFactory.create()
        self.admin = UserFactory.create()
        self.non_member = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.contribution = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.contributor
        })
        comment = CommentFactory.create(**{
            'commentto': self.contribution
        })
        response = CommentFactory.create(**{
            'commentto': self.contribution,
            'respondsto': comment
        })
        CommentFactory.create(**{
            'commentto': self.contribution,
            'respondsto': response
        })
        CommentFactory.create(**{
            'commentto': self.contribution,
            'respondsto': comment
        })
        CommentFactory.create(**{
            'commentto': self.contribution
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/projects/%s/contributions/%s/comments/' %
            (self.project.id, self.contribution.id)
        )
        force_authenticate(request, user=user)
        view = CommentsAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id
        ).render()

    def test_get_comments_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddCommentToPrivateProjectTest(APITestCase):
    def setUp(self):
        self.contributor = UserFactory.create()
        self.admin = UserFactory.create()
        self.non_member = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.contribution = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.contributor
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/contributions/%s/comments/' %
            (self.project.id, self.contribution.id),
            {'text': 'A comment to the contribution.'}
        )
        force_authenticate(request, user=user)
        view = CommentsAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id
        ).render()

    def test_add_comment_to_contribution_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_contribution_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_review_comment_to_contribution_with_contributor(self):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/contributions/%s/comments/' %
            (self.project.id, self.contribution.id),
            {
                'text': 'A review comment to the contribution.',
                'review_status': 'open'
            }
        )
        force_authenticate(request, user=self.contributor)
        view = CommentsAPIView.as_view()
        response = view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Observation.objects.get(pk=self.contribution.id).status,
            'review'
        )

    def test_add_closed_review_comment_to_contribution_with_contributor(self):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/contributions/%s/comments/' %
            (self.project.id, self.contribution.id),
            {
                'text': 'A review comment to the contribution.',
                'review_status': 'resolved'
            }
        )
        force_authenticate(request, user=self.contributor)
        view = CommentsAPIView.as_view()
        response = view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Observation.objects.get(pk=self.contribution.id).status,
            'active'
        )

    def test_add_comment_to_contribution_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_draft(self):
        self.contribution.status = 'draft'
        self.contribution.save()

        response = self.get_response(self.contribution.creator)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AddCommentToPublicProjectTest(APITestCase):
    def setUp(self):
        self.contributor = UserFactory.create()
        self.admin = UserFactory.create()
        self.non_member = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            **{'isprivate': False}
        )
        self.contribution = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.contributor
        })

    def get_response(self, user):
        if user.is_anonymous and not User.objects.filter(
                display_name='AnonymousUser').exists():
            UserFactory.create(display_name='AnonymousUser')

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/maps/all-contributions/%s/comments/' %
            (self.project.id, self.contribution.id),
            {'text': 'A comment to the contribution.'}
        )
        force_authenticate(request, user=user)
        view = CommentsAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id
        ).render()

    def test_add_comment_to_contribution_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_contribution_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_contribution_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_contribution_with_anonymous(self):
        response = self.get_response(AnonymousUser())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddCommentToWrongProjectContribution(APITestCase):
    def test(self):
        admin = UserFactory.create()
        project = ProjectFactory(add_admins=[admin])
        contribution = ObservationFactory.create()

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/contributions/%s/comments/' %
            (project.id, contribution.id),
            {'text': 'A comment to the contribution.'}
        )
        force_authenticate(request, user=admin)
        view = CommentsAPIView.as_view()
        response = view(
            request,
            project_id=project.id,
            contribution_id=contribution.id
        ).render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddResponseToProjectCommentTest(APITestCase):
    def test(self):
        admin = UserFactory.create()
        project = ProjectFactory(add_admins=[admin])
        contribution = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create(**{
            'commentto': contribution
        })

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/contributions/%s/comments/' %
            (project.id, contribution.id),
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        view = CommentsAPIView.as_view()
        response = view(
            request,
            project_id=project.id,
            contribution_id=contribution.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content).get('respondsto'),
            comment.id
        )


class AddResponseToWrongProjectCommentTest(APITestCase):
    def test(self):
        admin = UserFactory.create()
        project = ProjectFactory(add_admins=[admin])
        contribution = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/contributions/%s/comments/' %
            (project.id, contribution.id),
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        view = CommentsAPIView.as_view()
        response = view(
            request,
            project_id=project.id,
            contribution_id=contribution.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'The comment you try to respond to is not a comment to the '
            'contribution.'
        )


class DeleteProjectCommentTest(APITestCase):
    def setUp(self):
        self.contributor = UserFactory.create()
        self.admin = UserFactory.create()
        self.non_member = UserFactory.create()
        self.project = ProjectFactory(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            **{'isprivate': False}
        )
        self.contribution = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.contributor
        })
        self.comment = CommentFactory.create(**{
            'commentto': self.contribution
        })
        self.comment_to_remove = CommentFactory.create(**{
            'commentto': self.contribution,
            'creator': self.contributor
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.delete(
            '/api/projects/%s/contributions/%s/comments/%s/' %
            (self.project.id, self.contribution.id, self.comment_to_remove.id),
            {'text': 'A comment to the contribution.'}
        )
        force_authenticate(request, user=user)
        view = SingleCommentAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            contribution_id=self.contribution.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def test_delete_comment_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        contribution = Observation.objects.get(pk=self.contribution.id)
        self.assertIn(self.comment, contribution.comments.all())
        self.assertNotIn(self.comment_to_remove, contribution.comments.all())

    def test_delete_comment_with_comment_creator(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        contribution = Observation.objects.get(pk=self.contribution.id)
        self.assertIn(self.comment, contribution.comments.all())
        self.assertNotIn(self.comment_to_remove, contribution.comments.all())

    def test_delete_review_comment_with_comment_creator(self):
        self.comment_to_remove.review_status = 'open'
        self.comment_to_remove.save()
        self.contribution.status = 'review'
        self.contribution.save()

        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        contribution = Observation.objects.get(pk=self.contribution.id)
        self.assertEqual(contribution.status, 'active')

        self.assertIn(self.comment, contribution.comments.all())
        self.assertNotIn(self.comment_to_remove, contribution.comments.all())

    def test_delete_comment_but_not_change_status_from_pending(self):
        self.contribution.status = 'pending'
        self.contribution.save()

        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        contribution = Observation.objects.get(pk=self.contribution.id)
        self.assertEqual(contribution.status, 'pending')

    def test_delete_comment_and_change_status_from_review(self):
        self.contribution.status = 'review'
        self.contribution.save()

        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        contribution = Observation.objects.get(pk=self.contribution.id)
        self.assertEqual(contribution.status, 'active')

    def test_delete_one_review_comment_with_comment_creator(self):
        self.comment.review_status = 'open'
        self.comment.save()
        self.comment_to_remove.review_status = 'open'
        self.comment_to_remove.save()
        self.contribution.status = 'review'
        self.contribution.save()

        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        contribution = Observation.objects.get(pk=self.contribution.id)
        self.assertEqual(contribution.status, 'review')

        self.assertIn(self.comment, contribution.comments.all())
        self.assertNotIn(self.comment_to_remove, contribution.comments.all())

    def test_resolve_nested_comment_with_admin(self):
        self.comment.respondsto = self.comment_to_remove
        self.comment.review_status = 'open'
        self.comment.save()

        self.comment_to_remove.review_status = None
        self.comment_to_remove.save()

        self.contribution.status = 'review'
        self.contribution.save()

        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            Observation.objects.get(pk=self.contribution.id).status,
            'active'
        )


class DeleteWrongProjectComment(APITestCase):
    def test(self):
        admin = UserFactory.create()
        project = ProjectFactory(add_admins=[admin])
        contribution = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        request = factory.delete(
            '/api/projects/%s/contributions/%s/comments/%s/' %
            (project.id, contribution.id, comment.id),
            {'text': 'A comment to the contribution.'}
        )
        force_authenticate(request, user=admin)
        view = SingleCommentAPIView.as_view()
        response = view(
            request,
            project_id=project.id,
            contribution_id=contribution.id,
            comment_id=comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
