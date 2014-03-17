import json

from django.contrib.gis.geos import GEOSGeometry

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.decorators import (
    handle_exceptions_for_ajax
)

from projects.models import Project
from observationtypes.models import ObservationType

from .models import Location, Observation
from .serializers import ObservationSerializer


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
        location_data = properties.get('location')
        observation_data = properties.get('observation')

        project = Project.objects.as_contributor(request.user, project_id)
        try:
            observationtype = ObservationType.objects.get_single(
                request.user,
                project_id,
                observation_data.get('observationtype').get('id')
            )
        except ObservationType.DoesNotExist, error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'id' in location_data:
            location = Location.objects.get_single(
                request.user, project_id, location_data.get('id')
            )
        else:
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

        observation = Observation.objects.create(
            data=observation_data.get('data'),
            creator=request.user,
            location=location,
            project=project,
            observationtype=observationtype
        )

        serializer = ObservationSerializer()
        return Response(
            serializer.serialize(observation),
            status=status.HTTP_201_CREATED
        )
