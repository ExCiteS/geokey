from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.decorators import handle_exceptions_for_ajax
from core.exceptions import MalformedRequestData

from .serializers import (
    ContributionSerializer, LocationSerializer, CommentSerializer
)
from .models import Location, Comment
from projects.models import Project
from dataviews.models import View


# ############################################################################
#
# Locations
#
# ############################################################################

class Locations(APIView):
    """
    Public API endpoint for all locations in a project.
    /api/projects/:project_id/locations
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        """
        Returns a list of locations that can be used for contributions to the
        given project.
        """
        locations = Location.objects.get_list(request.user, project_id)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)


class SingleLocation(APIView):
    """
    Public API endpoint for a single location in a project.
    /api/projects/:project_id/locations/:location_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, location_id, format=None):
        location = Location.objects.get_single(
            request.user, project_id, location_id)
        serializer = LocationSerializer(
            location, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ############################################################################
#
# Observations
#
# ############################################################################

class Observations(APIView):
    """
    Public API endpoint for all observations in a project. Used to add new
    contributions to a project
    /api/projects/:project_id/observations
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, format=None):
        """
        Adds a new contribution to a project
        """
        data = request.DATA
        data['properties']['project'] = project_id
        serializer = ContributionSerializer(data=data, creator=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SingleObservation(APIView):
    def update_observation(self, request, observation, format=None):
        """
        Updates a single observation
        """
        serializer = ContributionSerializer(
            observation, data=request.DATA, creator=request.user
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions_for_ajax
    def delete_observation(self, request, observation, format=None):
        """
        Deletes a single observation
        """
        observation.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class SingleProjectObservation(SingleObservation):
    """
    Public API endpoint for updating a single observation in a project
    /api/projects/:project_id/observations/:observation_id
    """

    def get_object(self, user, project_id, observation_id):
        project = Project.objects.as_contributor(user, project_id)
        if project.is_admin(user):
            return project.observations.get(pk=observation_id)
        else:
            raise PermissionDenied('You are not an administrator of this '
                                   'project. You must therefore access '
                                   'observations through one of the views')

    @handle_exceptions_for_ajax
    def put(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.update_observation(request, observation, format=format)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.delete_observation(request, observation, format=format)


class SingleViewObservation(SingleObservation):
    """
    Public API endpoint for updating a single observation in a project
    /api/projects/:project_id/views/:view_id/observations/:observation_id
    """

    def get_object(self, user, project_id, view_id, observation_id):
        view = View.objects.get_single(user, project_id, view_id)
        if view.can_edit(user):
            return view.data.get(pk=observation_id)
        else:
            raise PermissionDenied(
                'You are not eligable to data of this view.')

    @handle_exceptions_for_ajax
    def put(self, request, project_id, view_id, observation_id, format=None):
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.update_observation(request, observation, format=format)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, observation_id,
               format=None):
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.delete_observation(request, observation, format=format)


class MyObservations(APIView):
    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        project = Project.objects.as_contributor(request.user, project_id)
        observations = project.observations.filter(creator=request.user)

        serializer = ContributionSerializer(observations, many=True)
        return Response(serializer.data)


class MySingleObservation(SingleObservation):
    def get_object(self, user, project_id, observation_id):
        try:
            project = Project.objects.as_contributor(user, project_id)
            return project.observations.filter(creator=user).get(
                pk=observation_id)
        except PermissionDenied:
            raise Project.DoesNotExist('You are not a contributor of this'
                                       'project.')

    @handle_exceptions_for_ajax
    def put(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.update_observation(request, observation, format=format)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.delete_observation(request, observation, format=format)


# ############################################################################
#
# Comments
#
# ############################################################################

class CommentApiView(object):
    def get_list_response(self, observation):
        comments = observation.comments.filter(respondsto=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_and_response(self, request, observation):
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
            creator=request.user
        )

        serializer = CommentSerializer(comment)
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


class ProjectComment(APIView):
    def get_object(self, request, project_id, observation_id):
        observation = Project.objects.get_single(
            request.user, project_id).observations.get(pk=observation_id)

        if observation.project.is_admin(request.user):
            return observation
        else:
            raise PermissionDenied('You are not an administrator of this '
                                   'project. You must therefore access '
                                   'observations through one of the views')


class ProjectComments(CommentApiView, ProjectComment):
    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id, format=None):
        """
        Returns a list of all comments of the observation
        """
        observation = self.get_object(request, project_id, observation_id)
        return self.get_list_response(observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = self.get_object(request, project_id, observation_id)
        return self.create_and_response(request, observation)


class ProjectSingleComment(CommentApiView, ProjectComment):
    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, comment_id,
               format=None):
        observation = self.get_object(request, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)


class ViewComment(APIView):
    def get_object(self, request, project_id, view_id, observation_id):
        return View.objects.get_single(
            request.user, project_id, view_id).data.get(pk=observation_id)


class ViewComments(CommentApiView, ViewComment):
    @handle_exceptions_for_ajax
    def get(self, request, project_id, view_id, observation_id, format=None):
        """
        Returns a list of all comments of the observation
        """
        observation = self.get_object(
            request, project_id, view_id, observation_id)
        return self.get_list_response(observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, view_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = self.get_object(
            request, project_id, view_id, observation_id)
        return self.create_and_response(request, observation)


class ViewSingleComment(CommentApiView, ViewComment):
    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, observation_id, comment_id,
               format=None):
        observation = self.get_object(
            request, project_id, view_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)
