from django.core.exceptions import PermissionDenied

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.core.exceptions import MalformedRequestData
from geokey.users.models import User
from .base import (
    SingleAllContribution, SingleGroupingContribution, SingleMyContribution
)
from ..models import Comment
from ..serializers import CommentSerializer


class CommentAbstractAPIView(APIView):
    """
    Abstract class for Comments views
    """
    def get_list_and_respond(self, user, observation):
        """
        Reponsds to a GET request with a list of all comments for an
        observation

        Parameters
        ----------
        user : geokey.users.models.User
            User authenticated with the request
        observation : geokey.contributions.models.Observation
            Observation the comments are requested for

        Returns
        -------
        rest_framework.response.Respones
            Contains the serialised comments
        """
        comments = observation.comments.filter(respondsto=None)
        serializer = CommentSerializer(
            comments, many=True, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_and_respond(self, request, observation):
        """
        Reponsds to a POST request by creating a comment

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        observation : geokey.contributions.models.Observation
            Observation the comments are requested for

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        if observation.status == 'draft':
            raise MalformedRequestData(
                'This contribution is a draft. You may not comment on drafts.'
            )

        user = request.user
        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        respondsto = request.DATA.get('respondsto') or None
        if respondsto is not None:
            try:
                respondsto = observation.comments.get(pk=respondsto)
            except Comment.DoesNotExist:
                raise MalformedRequestData('The comment you try to respond to'
                                           ' is not a comment to the '
                                           'observation.')

        review_status = request.DATA.get('review_status') or None
        if review_status == 'open' and observation.status != 'review':
            observation.update(None, user, status='review')

        comment = Comment.objects.create(
            text=request.DATA.get('text'),
            respondsto=respondsto,
            commentto=observation,
            creator=user,
            review_status=review_status
        )

        serializer = CommentSerializer(comment, context={'user': request.user})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update_and_respond(self, request, comment):
        """
        Reponsds to a PATCH request by updating a comment

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        comment : geokey.contributions.models.Comment
            Comment to be updated

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment

        Raises
        ------
        PermissionDenied
            if the user authenticated with the request is not allowed to
            update the comment
        """
        user = request.user
        data = request.DATA

        can_moderate = comment.commentto.project.can_moderate(request.user)
        is_owner = comment.creator == request.user

        if (is_owner or can_moderate):
            if data.get('review_status') == 'resolved' and not can_moderate:
                raise PermissionDenied('You are not a project moderator and '
                                       'therefore not eligable to resolve this'
                                       ' comment.')

            serializer = CommentSerializer(
                comment,
                data=data,
                partial=True,
                context={'user': user}
            )

            if serializer.is_valid():
                serializer.save()

                if (not comment.commentto.comments.filter(
                        review_status='open').exists()):
                    comment.commentto.update(None, user, status='active')

                return Response(serializer.data)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            raise PermissionDenied('You are neither the author if this comment'
                                   ' nor a project moderator and therefore'
                                   ' not eligable to edit this comment.')

    def delete_and_respond(self, request, comment):
        """
        Reponsds to a DELETE request by deleting a comment

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        comment : geokey.contributions.models.Comment
            Comment to be updated

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating success

        Raises
        ------
        PermissionDenied
            if the user authenticated with the request is not allowed to
            delete the comment
        """
        if (comment.creator == request.user or
                comment.commentto.project.can_moderate(request.user)):

            comment.delete()

            if (comment.review_status == 'open' and
                    not comment.commentto.comments.filter(
                        review_status='open').exists()):
                comment.commentto.update(None, request.user, status='active')

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied('You are neither the author if this comment'
                                   ' nor a project moderator and therefore'
                                   ' not eligable to delete this comment.')


class AllContributionsCommentsAPIView(
        CommentAbstractAPIView, SingleAllContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id):
        """
        Returns a list of all comments of the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, observation_id):
        """
        Adds a new comment to the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.create_and_respond(request, observation)


class AllContributionsSingleCommentAPIView(
        CommentAbstractAPIView, SingleAllContribution):

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, observation_id, comment_id):
        """
        Updates a comment

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(request.user, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.update_and_respond(request, comment)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, comment_id):
        """
        Deletes a comment from the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(request.user, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)


class GroupingContributionsCommentsAPIView(
        CommentAbstractAPIView, SingleGroupingContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, grouping_id, observation_id):
        """
        Returns a list of all comments of the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        observation = self.get_object(
            request.user, project_id, grouping_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, grouping_id, observation_id):
        """
        Adds a new comment to the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(
            request.user, project_id, grouping_id, observation_id)
        return self.create_and_respond(request, observation)


class GroupingContributionsSingleCommentAPIView(
        CommentAbstractAPIView, SingleGroupingContribution):

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, grouping_id, observation_id,
              comment_id):
        """
        Updates a comment

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(
            request.user, project_id, grouping_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.update_and_respond(request, comment)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, grouping_id, observation_id,
               comment_id):
        """
        Deletes a comment from the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(
            request.user, project_id, grouping_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)


class MyContributionsCommentsAPIView(
        CommentAbstractAPIView, SingleMyContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id):
        """
        Returns a list of all comments of the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, observation_id):
        """
        Adds a new comment to the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.create_and_respond(request, observation)


class MyContributionsSingleCommentAPIView(
        CommentAbstractAPIView, SingleMyContribution):

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, observation_id, comment_id,):
        """
        Updates a comment

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(request.user, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.update_and_respond(request, comment)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, comment_id,):
        """
        Deletes a comment from the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment
        """
        observation = self.get_object(request.user, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)
