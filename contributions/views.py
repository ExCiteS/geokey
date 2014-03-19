import json

from django.contrib.gis.geos import GEOSGeometry

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from projects.models import Project
from observationtypes.models import ObservationType

from core.decorators import (
    handle_exceptions_for_ajax
)

from .serializers import ContributionSerializer
from .models import Location, Observation


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
        properties = request.DATA.get('properties')
        location_data = properties.pop('location')
        observationtype_id = properties.pop('observationtype')

        project = Project.objects.as_contributor(request.user, project_id)
        try:
            observationtype = ObservationType.objects.get_single(
                request.user,
                project_id,
                observationtype_id
            )
        except ObservationType.DoesNotExist, error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        location = Location.objects.create(
            name=location_data.get('name'),
            description=location_data.get('description'),
            geometry=GEOSGeometry(
                json.dumps(request.DATA.get('geometry'))
            ),
            creator=request.user,
            private=location_data.get('private'),
            private_for_project=location_data.get('private_for_project')
        )

        observation = Observation.create(
            data=properties,
            creator=request.user,
            location=location,
            project=project,
            observationtype=observationtype
        )

        serializer = ContributionSerializer()
        return Response(
            serializer.serialize(observation),
            status=status.HTTP_201_CREATED
        )


class ProjectSingleObservation(APIView):
    """
    Public API endpoint for updating a single observation in a project
    /api/projects/:project_id/observations/:observationtype_id
    """
    def put(self, request, project_id, observation_id, format=None):
        observation = Observation.objects.as_contributor(
            request.user, project_id, observation_id
        )
        properties = request.DATA.get('properties')
        observation.update(data=properties, creator=request.user)
        serializer = ContributionSerializer()
        return Response(
            serializer.serialize(observation),
            status=status.HTTP_200_OK
        )

    def delete(self, request, project_id, observation_id, format=None):
        observation = Observation.objects.as_contributor(
            request.user, project_id, observation_id
        )
        observation.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
