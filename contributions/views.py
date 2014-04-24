from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.decorators import (
    handle_exceptions_for_ajax
)

from .serializers import (
    ContributionSerializer, LocationSerializer, CommentSerializer
)
from .models import Observation, Location, Comment


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
    def post(self, request, project_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = Observation.objects.as_contributor(
            request.user, project_id, observation_id
        )
        comment = Comment.objects.create(
            text=request.DATA.get('text'),
            commentto=observation,
            creator=request.user
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
