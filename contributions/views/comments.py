from django.core.exceptions import PermissionDenied

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.decorators import handle_exceptions_for_ajax
from core.exceptions import MalformedRequestData
from users.models import User
from .base import (
    SingleAllContribution, SingleGroupingContribution, SingleMyContribution
)
from ..models import Comment
from ..serializers import CommentSerializer


class CommentAbstractAPIView(APIView):
    def get_list_and_respond(self, user, observation):
        comments = observation.comments.filter(respondsto=None)
        serializer = CommentSerializer(
            comments, many=True, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_and_respond(self, request, observation):
        user = request.user
        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        respondsto = None
        if request.DATA.get('respondsto') is not None:
            try:
                respondsto = observation.comments.get(
                    pk=request.DATA.get('respondsto'))
            except Comment.DoesNotExist:
                raise MalformedRequestData('The comment you try to respond to'
                                           ' is not a comment to the '
                                           'observation.')

        comment = Comment.objects.create(
            text=request.DATA.get('text'),
            respondsto=respondsto,
            commentto=observation,
            creator=user
        )

        serializer = CommentSerializer(comment, context={'user': request.user})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_and_respond(self, request, comment):
        if (comment.creator == request.user or
                comment.commentto.project.is_admin(request.user)):
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied('You are neither the author if this comment'
                                   ' nor a project administrator and therefore'
                                   ' not eligable to delete this comment.')


class AllContributionsCommentsAPIView(
        CommentAbstractAPIView, SingleAllContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id, format=None):
        """
        Returns a list of all comments of the observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.create_and_respond(request, observation)


class AllContributionsSingleCommentAPIView(
        CommentAbstractAPIView, SingleAllContribution):

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, comment_id,
               format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)


class GroupingContributionsCommentsAPIView(
        CommentAbstractAPIView, SingleGroupingContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, view_id, observation_id, format=None):
        """
        Returns a list of all comments of the observation
        """
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, view_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.create_and_respond(request, observation)


class GroupingContributionsSingleCommentAPIView(
        CommentAbstractAPIView, SingleGroupingContribution):

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, observation_id, comment_id,
               format=None):
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)


class MyContributionsCommentsAPIView(
        CommentAbstractAPIView, SingleMyContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.create_and_respond(request, observation)


class MyContributionsSingleCommentAPIView(
        CommentAbstractAPIView, SingleMyContribution):

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, comment_id,
               format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)
