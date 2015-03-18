from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from geokey.core.decorators import handle_exceptions_for_ajax

from ..models.locations import Location
from ..serializers import LocationSerializer


class Locations(APIView):
    """
    Public API endpoint for all locations in a project.
    /api/projects/:project_id/locations/
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        """
        Returns a list of locations that can be used for contributions to the
        given project.
        """
        q = request.GET.get('query')
        locations = Location.objects.get_list(request.user, project_id)

        if q is not None:
            locations = locations.filter(
                Q(name__icontains=q.lower()) |
                Q(description__icontains=q.lower())
            )

        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)


class SingleLocation(APIView):
    """
    Public API endpoint for a single location in a project.
    /api/projects/:project_id/locations/:location_id/
    """
    @handle_exceptions_for_ajax
    def patch(self, request, project_id, location_id):
        location = Location.objects.get_single(
            request.user, project_id, location_id)
        serializer = LocationSerializer(
            location, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
