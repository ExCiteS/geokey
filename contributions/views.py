from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.decorators import handle_exceptions_for_ajax
from core.exceptions import MalformedRequestData

from .serializers import (
    ContributionSerializer, LocationSerializer, CommentSerializer
)
from .models import Observation, Location, Comment
from projects.models import Project


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
    """
    Public API endpoint for updating a single observation in a project
    /api/projects/:project_id/observations/:observationtype_id
    """

    @handle_exceptions_for_ajax
    def put(self, request, project_id, observation_id, format=None):
        """
        Updates a single observation
        """
        observation = Observation.objects.as_contributor(
            request.user, project_id, observation_id
        )
        serializer = ContributionSerializer(
            observation, data=request.DATA, creator=request.user
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, format=None):
        """
        Deletes a single observation
        """
        observation = Observation.objects.as_contributor(
            request.user, project_id, observation_id
        )
        observation.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class Comments(APIView):
    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id, format=None):
        """
        Returns a list of all comments of the observation
        """
        observation = Project.objects.get(
            pk=project_id).observations.get(pk=observation_id)

        if observation.project.is_admin(request.user):
            comments = observation.comments.filter(respondsto=None)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied('You are not an administrator of this '
                                   'project. You must therefore access '
                                   'observations thorugh one of the views')

    @handle_exceptions_for_ajax
    def post(self, request, project_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = Observation.objects.as_contributor(
            request.user, project_id, observation_id
        )

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


class SingleComment(APIView):
    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, comment_id,
               format=None):
        observation = Observation.objects.as_contributor(
            request.user, project_id, observation_id
        )
        comment = observation.comments.get(pk=comment_id)
        if (comment.creator == request.user or
                observation.project.is_admin(request.user)):
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied('You are neither the author if this comment'
                                   ' nor a project administrator and therefore'
                                   ' not eligable to delete this comment.')
