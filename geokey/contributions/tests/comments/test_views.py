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

from geokey.projects.tests.model_factories import UserF, ProjectF
from geokey.projects.models import Project
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.datagroupings.tests.model_factories import (
    GroupingFactory, RuleFactory
)
from geokey.contributions.models import Comment, Observation
from geokey.datagroupings.models import Grouping

from geokey.users.tests.model_factories import (
    UserGroupF, GroupingUserGroupFactory
)
from ..model_factories import ObservationFactory, CommentFactory

from geokey.contributions.views.comments import (
    AllContributionsSingleCommentAPIView,
    GroupingContributionsSingleCommentAPIView,
    AllContributionsCommentsAPIView, MyContributionsCommentsAPIView,
    MyContributionsSingleCommentAPIView, GroupingContributionsCommentsAPIView,
    CommentAbstractAPIView
)


class CommentAbstractAPIViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.moderator = UserF.create()
        self.commenter = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator, self.commenter]
        )
        self.moderators = UserGroupF(add_users=[self.moderator], **{
            'project': self.project,
            'can_moderate': True
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'status': 'active'
        })
        self.comment = CommentFactory.create(**{
            'commentto': self.observation,
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
            'observation_id': self.observation.id
        })
        request = self.factory.post(url, {'text': 'Comment'})
        request.user = self.admin
        request.DATA = {'text': 'Comment'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.create_and_respond(request, self.observation)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Comment')

    def test_create_reviewcomment_with_admin(self):
        url = reverse('api:project_comments', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.post(
            url, {'text': 'Comment', 'review_status': 'open'}
        )
        request.user = self.admin
        request.DATA = {'text': 'Comment', 'review_status': 'open'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.create_and_respond(request, self.observation)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Comment')
        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'review')

    def test_create_reviewcomment_to_empty_obs_with_admin(self):
        self.observation.properties = None
        self.observation.save()

        url = reverse('api:project_comments', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id
        })
        request = self.factory.post(
            url, {'text': 'Comment', 'review_status': 'open'}
        )
        request.user = self.admin
        request.DATA = {'text': 'Comment', 'review_status': 'open'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.create_and_respond(request, self.observation)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Comment')
        ref = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(ref.status, 'review')

    def test_update_comment_with_admin(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.admin
        request.DATA = {'text': 'Updated'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.comment)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Updated')
        self.assertEqual(
            Comment.objects.get(pk=self.comment.id).text,
            'Updated'
        )

    def test_update_comment_with_commenter(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.commenter
        request.DATA = {'text': 'Updated'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.comment)
        )
        self.assertEqual(json.loads(response.content).get('text'), 'Updated')
        self.assertEqual(
            Comment.objects.get(pk=self.comment.id).text,
            'Updated'
        )

    def test_update_comment_with_moderator(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.moderator
        request.DATA = {'text': 'Updated'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.comment)
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
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.creator
        request.DATA = {'text': 'Updated'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.comment)
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

        grouping = GroupingFactory(**{
            'project': self.project,
            'isprivate': False,
        })
        RuleFactory.create(**{
            'category': self.observation.category,
            'grouping': grouping
        })

        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(
            url, {'text': 'Updated', 'review_status': 'blah'}
        )
        force_authenticate(request, user=self.commenter)

        view = AllContributionsSingleCommentAPIView.as_view()
        response = view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id,
            comment_id=self.comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentAbstractAPIViewResolveTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.creator = UserF.create()
        self.moderator = UserF.create()
        self.commenter = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.creator, self.commenter]
        )
        self.moderators = UserGroupF(add_users=[self.moderator], **{
            'project': self.project,
            'can_moderate': True
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'status': 'review'
        })
        self.comment = CommentFactory.create(**{
            'commentto': self.observation,
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
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.admin
        request.DATA = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.comment)
        )
        self.assertEqual(
            json.loads(response.content).get('review_status'),
            'resolved'
        )
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    def test_resolve_comment_with_invalid_review_status(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.admin
        request.DATA = {'review_status': 'closed'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.comment)
        )

        ref = Comment.objects.get(pk=self.comment.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ref.review_status, 'open')

    def test_resolve_one_of_two_comment_with_admin(self):
        CommentFactory.create(**{
            'commentto': self.observation,
            'creator': self.creator,
            'review_status': 'open'
        })

        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.admin
        request.DATA = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.comment)
        )
        self.assertEqual(
            json.loads(response.content).get('review_status'),
            'resolved'
        )
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'review'
        )

    def test_resolve_comment_with_moderator(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.moderator
        request.DATA = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        response = self.render(
            view.update_and_respond(request, self.comment)
        )
        self.assertEqual(
            json.loads(response.content).get('review_status'),
            'resolved'
        )
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    @raises(PermissionDenied)
    def test_resolve_comment_with_creator(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.creator
        request.DATA = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        view.update_and_respond(request, self.comment)

    @raises(PermissionDenied)
    def test_resolve_comment_with_commenter(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = self.commenter
        request.DATA = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        view.update_and_respond(request, self.comment)

    @raises(PermissionDenied)
    def test_resolve_comment_with_anonymous(self):
        url = reverse('api:project_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment.id
        })
        request = self.factory.patch(url, {'text': 'Updated'})
        request.user = AnonymousUser()
        request.DATA = {'review_status': 'resolved'}

        view = CommentAbstractAPIView()
        view.update_and_respond(request, self.comment)


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

        category = CategoryFactory(**{'project': self.project})

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.creator,
            'category': category
        })

        self.view = GroupingFactory(**{'project': self.project})
        RuleFactory(**{
            'grouping': self.view,
            'category': category}
        )

    def test_get_object_with_admin(self):
        view = GroupingContributionsSingleCommentAPIView()
        observation = view.get_object(
            self.admin, self.project.id, self.view.id, self.observation.id)
        self.assertEqual(observation, self.observation)

    @raises(Grouping.DoesNotExist)
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
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': group}
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
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': group}
        )
        view = GroupingContributionsSingleCommentAPIView()
        view.get_object(
            view_member, self.observation.project.id,
            self.view.id, self.observation.id
        )


class GetProjectComments(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.contributor
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
        request = factory.get(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id)
        )
        force_authenticate(request, user=user)
        view = AllContributionsCommentsAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_get_comments_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_with_view_member(self):
        view_member = UserF.create()

        GroupingFactory(add_viewers=[view_member], **{
            'project': self.project
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddCommentToPrivateProjectTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.contributor
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = AllContributionsCommentsAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_review_comment_to_observation_with_contributor(self):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id),
            {
                'text': 'A review comment to the observation',
                'review_status': 'open'
            }
        )
        force_authenticate(request, user=self.contributor)
        view = AllContributionsCommentsAPIView.as_view()
        response = view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'review'
        )

    def test_add_closed_review_comment_to_observation_with_contributor(self):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id),
            {
                'text': 'A review comment to the observation',
                'review_status': 'resolved'
            }
        )
        force_authenticate(request, user=self.contributor)
        view = AllContributionsCommentsAPIView.as_view()
        response = view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Observation.objects.get(pk=self.observation.id).status,
            'active'
        )

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        GroupingFactory(add_viewers=[view_member], **{
            'project': self.project
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_draft(self):
        self.observation.status = 'draft'
        self.observation.save()

        response = self.get_response(self.observation.creator)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AddCommentToPublicProjectTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            **{'isprivate': False}
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.contributor
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/maps/all-contributions/%s/comments/' %
            (self.project.id, self.observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = AllContributionsCommentsAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        GroupingFactory(add_viewers=[view_member], **{
            'project': self.project
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_anonymous(self):
        response = self.get_response(AnonymousUser())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        grouping = GroupingFactory(**{
            'project': self.project,
            'isprivate': False,
        })
        RuleFactory.create(**{
            'category': self.observation.category,
            'grouping': grouping
        })
        response = self.get_response(AnonymousUser())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddCommentToWrongProjectObservation(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        observation = ObservationFactory.create()

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (project.id, observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=admin)
        view = AllContributionsCommentsAPIView.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id
        ).render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddResponseToProjectCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        observation = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create(**{
            'commentto': observation
        })

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (project.id, observation.id),
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        view = AllContributionsCommentsAPIView.as_view()
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


class AddResponseToWrongProjectCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        observation = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (project.id, observation.id),
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        view = AllContributionsCommentsAPIView.as_view()
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


class DeleteProjectCommentTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            **{'isprivate': False}
        )
        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'creator': self.contributor
        })
        self.comment = CommentFactory.create(**{
            'commentto': self.observation
        })
        self.comment_to_remove = CommentFactory.create(**{
            'commentto': self.observation,
            'creator': self.contributor
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.delete(
            '/api/projects/%s/observations/%s/comments/%s/' %
            (self.project.id, self.observation.id, self.comment_to_remove.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = AllContributionsSingleCommentAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def test_delete_comment_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_comment_creator(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_review_comment_with_comment_creator(self):
        self.comment_to_remove.review_status = 'open'
        self.comment_to_remove.save()
        self.observation.status = 'review'
        self.observation.save()

        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(observation.status, 'active')

        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_one_review_comment_with_comment_creator(self):
        self.comment.review_status = 'open'
        self.comment.save()
        self.comment_to_remove.review_status = 'open'
        self.comment_to_remove.save()
        self.observation.status = 'review'
        self.observation.save()

        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertEqual(observation.status, 'review')

        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())


class DeleteWrongProjectComment(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        observation = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        request = factory.delete(
            '/api/projects/%s/observations/%s/comments/%s/' %
            (project.id, observation.id, comment.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=admin)
        view = AllContributionsSingleCommentAPIView.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id,
            comment_id=comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetMyObservationComments(APITestCase):
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
        view = MyContributionsCommentsAPIView.as_view()
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

        GroupingFactory(add_viewers=[view_member], **{
            'project': self.project
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_with_creator(self):
        response = self.get_response(self.creator)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AddMyObservationCommentTest(APITestCase):
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
        view = MyContributionsCommentsAPIView.as_view()
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
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        GroupingFactory(add_viewers=[view_member], **{
            'project': self.project
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_creator(self):
        response = self.get_response(self.creator)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddCommentToWrongMyObservation(APITestCase):
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
        view = MyContributionsCommentsAPIView.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id
        ).render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddResponseToMyObservationCommentTest(APITestCase):
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
        view = MyContributionsCommentsAPIView.as_view()
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


class AddResponseToWrongMyObservationCommentTest(APITestCase):
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
        view = MyContributionsCommentsAPIView.as_view()
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


class MyObservationCommentTest(APITestCase):
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

    def update_comment(self, user):
        factory = APIRequestFactory()
        url = reverse('api:myobservations_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment_to_remove.id
        })
        request = factory.patch(
            url,
            {'text': 'new text'}
        )
        force_authenticate(request, user=user)
        view = MyContributionsSingleCommentAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def delete_comment(self, user):
        factory = APIRequestFactory()
        url = reverse('api:myobservations_single_comment', kwargs={
            'project_id': self.project.id,
            'observation_id': self.observation.id,
            'comment_id': self.comment_to_remove.id
        })
        request = factory.delete(url)
        force_authenticate(request, user=user)
        view = MyContributionsSingleCommentAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def test_update_comment_comment_creator(self):
        response = self.update_comment(self.creator)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_comment_with_admin(self):
        response = self.delete_comment(self.admin)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_contributor(self):
        response = self.delete_comment(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_comment_creator(self):
        response = self.delete_comment(self.creator)
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
        view = MyContributionsSingleCommentAPIView.as_view()
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


class DeleteWrongMyObservationComment(APITestCase):
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
        view = MyContributionsSingleCommentAPIView.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id,
            comment_id=comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetCommentsView(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        category = CategoryFactory(**{'project': self.project})
        self.view = GroupingFactory(**{'project': self.project})
        RuleFactory(**{
            'grouping': self.view,
            'category': category}
        )

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'category': category
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
                'grouping_id': self.view.id,
                'observation_id': self.observation.id
            }
        )
        request = factory.get(url)
        force_authenticate(request, user=user)
        view = GroupingContributionsCommentsAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            grouping_id=self.view.id,
            observation_id=self.observation.id
        ).render()

    def test_get_comments_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_with_view_member(self):
        view_member = UserF.create()
        GroupingFactory.create(
            add_viewers=[view_member],
            **{'project': self.project}
        )

        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_with_view_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_with_view_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddCommentToViewTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        category = CategoryFactory(**{'project': self.project})
        self.view = GroupingFactory(**{'project': self.project})
        RuleFactory(**{
            'grouping': self.view,
            'category': category
        })

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'category': category
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': self.project.id,
                'grouping_id': self.view.id,
                'observation_id': self.observation.id
            }
        )
        request = factory.post(url, {'text': 'A comment to the observation'})
        force_authenticate(request, user=user)
        view = GroupingContributionsCommentsAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            grouping_id=self.view.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        group = UserGroupF.create(
            add_users=[view_member],
            **{'project': self.view.project}
        )
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': group}
        )
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddCommentToWrongGroupingObservation(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(
            add_admins=[admin]
        )
        observation = ObservationFactory.create()
        category = CategoryFactory(**{'project': project})
        view = GroupingFactory(**{'project': project})
        RuleFactory(**{'grouping': view, 'category': category})

        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': project.id,
                'grouping_id': view.id,
                'observation_id': observation.id
            }
        )
        factory = APIRequestFactory()
        request = factory.post(url, {'text': 'A comment to the observation'})
        force_authenticate(request, user=admin)
        dataview = GroupingContributionsCommentsAPIView.as_view()
        response = dataview(
            request,
            project_id=project.id,
            grouping_id=view.id,
            observation_id=observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddResponseToGroupingCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(
            add_admins=[admin]
        )
        category = CategoryFactory(**{'project': project})
        view = GroupingFactory(**{'project': project})
        RuleFactory(**{'grouping': view, 'category': category})

        observation = ObservationFactory.create(**{
            'project': project,
            'category': category
        })
        comment = CommentFactory.create(**{
            'commentto': observation
        })

        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': project.id,
                'grouping_id': view.id,
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
        dataview = GroupingContributionsCommentsAPIView.as_view()
        response = dataview(
            request,
            project_id=project.id,
            grouping_id=view.id,
            observation_id=observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content).get('respondsto'),
            comment.id
        )


class AddResponseToWrongGroupingCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(
            add_admins=[admin]
        )
        category = CategoryFactory(**{'project': project})
        view = GroupingFactory(**{'project': project})
        RuleFactory(**{'grouping': view, 'category': category})

        observation = ObservationFactory.create(**{
            'project': project,
            'category': category
        })
        comment = CommentFactory.create()

        url = reverse(
            'api:view_comments',
            kwargs={
                'project_id': project.id,
                'grouping_id': view.id,
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
        dataview = GroupingContributionsCommentsAPIView.as_view()
        response = dataview(
            request,
            project_id=project.id,
            grouping_id=view.id,
            observation_id=observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'The comment you try to respond to is not a comment to the '
            'observation.'
        )


class DeleteGroupingCommentTest(APITestCase):
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
        category = CategoryFactory(**{'project': self.project})
        self.view = GroupingFactory(**{'project': self.project})
        group = UserGroupF.create(
            add_users=[self.view_member, self.commentor],
            **{'project': self.view.project}
        )
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': group}
        )
        RuleFactory(
            **{'grouping': self.view, 'category': category}
        )

        self.observation = ObservationFactory.create(**{
            'project': self.project,
            'category': category
        })

        self.comment = CommentFactory.create(**{
            'commentto': self.observation
        })
        self.comment_to_remove = CommentFactory.create(**{
            'commentto': self.observation,
            'creator': self.commentor
        })

    def delete_comment(self, user):
        factory = APIRequestFactory()
        url = reverse(
            'api:view_single_comment',
            kwargs={
                'project_id': self.project.id,
                'grouping_id': self.view.id,
                'observation_id': self.observation.id,
                'comment_id': self.comment_to_remove.id
            }
        )
        request = factory.delete(url)
        force_authenticate(request, user=user)
        view = GroupingContributionsSingleCommentAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            grouping_id=self.view.id,
            observation_id=self.observation.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def update_comment(self, user):
        factory = APIRequestFactory()
        url = reverse(
            'api:view_single_comment',
            kwargs={
                'project_id': self.project.id,
                'grouping_id': self.view.id,
                'observation_id': self.observation.id,
                'comment_id': self.comment_to_remove.id
            }
        )
        request = factory.patch(url, {'text': 'new text'})
        force_authenticate(request, user=user)
        view = GroupingContributionsSingleCommentAPIView.as_view()
        return view(
            request,
            project_id=self.project.id,
            grouping_id=self.view.id,
            observation_id=self.observation.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def test_update_comment_with_admin(self):
        response = self.update_comment(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_comment_with_admin(self):
        response = self.delete_comment(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_view_comment_creator(self):
        response = self.delete_comment(self.commentor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_view_member(self):
        response = self.delete_comment(self.view_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are neither the author if this comment nor a project '
            'moderator and therefore not eligable to delete this comment.'
        )

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_non_member(self):
        response = self.delete_comment(self.non_member)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())


class DeleteWrongGroupingComment(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF(add_admins=[admin])
        category = CategoryFactory(**{'project': project})
        view = GroupingFactory(**{'project': project})
        RuleFactory(**{'grouping': view, 'category': category})

        observation = ObservationFactory.create(**{
            'project': project,
            'category': category
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        factory = APIRequestFactory()
        url = reverse(
            'api:view_single_comment',
            kwargs={
                'project_id': project.id,
                'grouping_id': view.id,
                'observation_id': observation.id,
                'comment_id': comment.id
            }
        )
        request = factory.delete(url)
        force_authenticate(request, user=admin)
        dataview = GroupingContributionsSingleCommentAPIView.as_view()
        response = dataview(
            request,
            project_id=project.id,
            grouping_id=view.id,
            observation_id=observation.id,
            comment_id=comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
