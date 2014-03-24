from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.decorators import (
    handle_exceptions_for_ajax
)

from .serializers import ContributionSerializer
from .models import Observation


class ProjectObservations(APIView):
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


class ProjectSingleObservation(APIView):
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
