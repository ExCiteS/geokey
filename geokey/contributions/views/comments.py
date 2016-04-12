"""Views for comments of categories."""

from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.core.exceptions import MalformedRequestData
from geokey.users.models import User

from .base import SingleAllContribution
from ..models import Comment
from ..serializers import CommentSerializer


class CommentAbstractAPIView(APIView):
    """Abstract class for comments."""

    def get_user(self, request):
        """
        Get user of a request.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        geokey.users.models.User
            User of a request.
        """
        user = request.user

        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        return user

    def get_comment(self, contribution, comment_id):
        """
        Get comment of a contribution.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution to retrieve the comment from.
        comment_id : int
            Identifies the comment in the database.

        Returns
        -------
        geokey.contributions.models.Comment
            Comment of a contribution.
        """
        return contribution.comments\
            .select_related('creator')\
            .prefetch_related('responses')\
            .get(pk=comment_id)

    def get_list_and_respond(self, request, contribution):
        """
        Respond to a GET request with a list of all comments.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution the comments are requested for.

        Returns
        -------
        rest_framework.response.Respones
            Contains the serialized comments.
        """
        serializer = CommentSerializer(
            contribution.comments.filter(respondsto=None),
            many=True,
            context={'user': self.get_user(request)}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_and_respond(self, request, contribution):
        """
        Respond to a POST request by creating a comment.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution the comment should be added to.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialized comment.

        Raises
        ------
        MalformedRequestData
            When contribution is a draft or comment does not belong to the
            contribution.
        """
        user = self.get_user(request)

        if contribution.status == 'draft':
            raise MalformedRequestData(
                'This contribution is a draft. You may not comment on drafts.'
            )

        respondsto = request.data.get('respondsto') or None
        if respondsto:
            try:
                respondsto = contribution.comments.get(pk=respondsto)
            except Comment.DoesNotExist:
                raise MalformedRequestData(
                    'The comment you try to respond to is not a comment '
                    'to the contribution.'
                )

        review_status = request.data.get('review_status') or None
        if review_status == 'open' and contribution.status != 'review':
            contribution.update(None, user, status='review')

        comment = Comment.objects.create(
            text=request.data.get('text'),
            commentto=contribution,
            respondsto=respondsto,
            creator=user,
            review_status=review_status
        )

        serializer = CommentSerializer(comment, context={'user': user})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update_and_respond(self, request, contribution, comment):
        """
        Respond to a PATCH request by updating the comment.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution of a comment.
        comment : geokey.contributions.models.Comment
            Comment to be updated.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialized comment.

        Raises
        ------
        PermissionDenied
            When user is not allowed to update the comment.
        """
        user = self.get_user(request)
        data = request.data

        is_owner = comment.creator == user
        can_moderate = contribution.project.can_moderate(user)

        if is_owner or can_moderate:
            if data.get('review_status') == 'resolved' and not can_moderate:
                raise PermissionDenied(
                    'You are not a project moderator and therefore not '
                    'eligable to resolve this comment.'
                )

            serializer = CommentSerializer(
                comment,
                data=data,
                partial=True,
                context={'user': user}
            )

            if serializer.is_valid():
                serializer.save()

                if (not contribution.comments.filter(
                        review_status='open').exists()):
                    contribution.update(None, user, status='active')

                return Response(serializer.data)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            raise PermissionDenied(
                'You are neither the author if this comment nor a project '
                'moderator and therefore not eligable to edit it.'
            )

    def delete_and_respond(self, request, contribution, comment):
        """
        Respond to a DELETE request by deleting the comment.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution of a comment.
        comment : geokey.contributions.models.Comment
            Comment to be deleted.

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating success.

        Raises
        ------
        PermissionDenied
            When user is not allowed to delete the comment.
        """
        user = self.get_user(request)

        if comment.creator == user or contribution.project.can_moderate(user):
            comment.delete()

            if (contribution.status == 'review' and
                    not contribution.comments.filter(
                        review_status='open').exists()):
                contribution.update(None, user, status='active')

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                'You are neither the author if this comment nor a project '
                'moderator and therefore not eligable to delete it.'
            )


class CommentsAPIView(SingleAllContribution, CommentAbstractAPIView):
    """Public API for all comments."""

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id):
        """
        Handle GET request.

        Return a list of all comments of the contribution.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments.
        """
        contribution = self.get_contribution(
            request.user,
            project_id,
            contribution_id
        )

        return self.get_list_and_respond(request, contribution)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, contribution_id):
        """
        Handle POST request.

        Add a new comment to the contribution.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comment.
        """
        contribution = self.get_contribution(
            request.user,
            project_id,
            contribution_id
        )

        return self.create_and_respond(request, contribution)


class SingleCommentAPIView(SingleAllContribution, CommentAbstractAPIView):
    """Public API for a single comment."""

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, contribution_id, comment_id):
        """
        Handle PATCH request.

        Update the comment.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.
        comment_id : int
            Identifies the comment in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialized comment.
        """
        contribution = self.get_contribution(
            request.user,
            project_id,
            contribution_id
        )
        comment = self.get_comment(contribution, comment_id)

        return self.update_and_respond(request, contribution, comment)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, contribution_id, comment_id):
        """
        Handle DELETE request.

        Delete the comment.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.
        comment_id : int
            Identifies the comment in the database.

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating success.
        """
        contribution = self.get_contribution(
            request.user,
            project_id,
            contribution_id
        )
        comment = self.get_comment(contribution, comment_id)

        return self.delete_and_respond(request, contribution, comment)
